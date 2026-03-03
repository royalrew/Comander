from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from sqlalchemy.orm import Session

import database
import models
from cfo import cfo
from sqlalchemy import text

# Ensure database tables exist
models.Base.metadata.create_all(bind=database.engine)

# Auto-migrate: Add reminder_sent column if missing
try:
    with database.engine.begin() as conn:
        conn.execute(text("ALTER TABLE events ADD COLUMN reminder_sent BOOLEAN DEFAULT FALSE"))
except Exception:
    pass # Column already exists or other error

app = FastAPI(title="Sintari Commander API", version="0.1.0")

# Import the new LangGraph Swarm Router
from router import api_router
app.include_router(api_router)

# Allow the Next.js dashboard to access this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health")
async def health_check():
    return {"status": "online", "pulse": "stable"}

@app.get("/api/v1/cfo/status")
async def get_cfo_status():
    """Returns real-time financial data from the CFO module."""
    return {
        "current_spend_usd": cfo.current_daily_spend,
        "max_spend_usd": cfo.max_daily_spend,
        "revenue_usd": 0.00, # Placeholder for Stripe integration
        "circuit_breaker_active": cfo.current_daily_spend > cfo.max_daily_spend
    }

@app.get("/api/v1/cortex/status")
async def get_cortex_status():
    """Returns the core heartbeat and overall memory usage."""
    count = 0
    try:
        from memory_module import memory_bank
        if memory_bank.client and memory_bank.client.indices.exists(index="commander_core_memory"):
            count = memory_bank.client.count(index="commander_core_memory")['count']
    except Exception as e:
        print(f"Error checking OpenSearch count: {e}")
        
    return {
        "heartbeat": "stable",
        "active_model": "gpt-4o",
        "memory_usage": f"{count}/10000 vectors"
    }

@app.get("/api/v1/cortex/logs")
async def get_cortex_logs():
    """Returns the last 50 rows from the system_logs Postgres table."""
    from database import SessionLocal
    from models import SystemLogDB
    db = SessionLocal()
    try:
        logs = db.query(SystemLogDB).order_by(SystemLogDB.timestamp.desc()).limit(50).all()
        return {"logs": [{"id": l.id, "timestamp": l.timestamp.isoformat(), "action": l.action_type, "details": l.details} for l in logs]}
    except Exception as e:
        return {"logs": [], "error": str(e)}
    finally:
        db.close()

@app.get("/api/v1/cortex/memories")
async def get_cortex_memories():
    """Returns the last 5 indexed thoughts from OpenSearch."""
    from memory_module import memory_bank
    if not memory_bank.client: return {"memories": []}
    
    search_query = {
        "size": 5,
        "query": {"match_all": {}},
        "sort": [{"timestamp": {"order": "desc"}}],
        "_source": ["text", "category", "timestamp"]
    }
    try:
        if memory_bank.client.indices.exists(index="commander_core_memory"):
            response = memory_bank.client.search(index="commander_core_memory", body=search_query)
            hits = response["hits"]["hits"]
            return {"memories": [{"id": h["_id"], **h["_source"]} for h in hits]}
        return {"memories": []}
    except Exception as e:
        return {"memories": [], "error": str(e)}

@app.get("/api/v1/tools/status")
async def get_tools_status():
    """Returns the current state of the AI's autonomous tools."""
    # This will eventually map to a DB setting, hardcoded for UI testing
    return {
        "tools": [
            {
                "id": "file_observer",
                "name": "File Observer",
                "active": True,
                "module": "observer.py"
            },
            {
                "id": "the_surgeon",
                "name": "The Surgeon",
                "active": True,
                "module": "surgeon.py",
                "critical": True
            },
            {
                "id": "omni_scraper",
                "name": "Omni-Scraper",
                "active": False,
                "module": "scraper.py"
            }
        ],
        "allowed_domains": [
            "https://docs.microsoft.com/*",
            "https://stripe.com/docs/*",
            "https://nextjs.org/docs/*"
        ]
    }

class CalendarEventCreate(BaseModel):
    start_date: str
    start_time: str
    description: str
    end_time: str | None = None
    is_reminder: bool = True
    category: str = "General"
    priority: str = "Medium"
    agent_id: str | None = None
    location: str | None = None
    color: str | None = None

@app.get("/api/v1/calendar")
async def get_all_calendar_events():
    """Returns all events from the calendar database for the Dashboard UI."""
    from calendar_agent import calendar_agent
    try:
        events = calendar_agent._load_events()
        return {"status": "success", "events": events}
    except Exception as e:
        return {"status": "error", "message": str(e), "events": []}

@app.post("/api/v1/calendar")
async def create_calendar_event(event: CalendarEventCreate):
    """Allows the Dashboard UI to manually inject events into the AI's calendar."""
    from calendar_agent import calendar_agent
    try:
        success = calendar_agent.add_event(
            start_date=event.start_date,
            start_time=event.start_time,
            description=event.description,
            end_time=event.end_time,
            is_reminder=event.is_reminder,
            category=event.category,
            priority=event.priority,
            agent_id=event.agent_id,
            location=event.location,
            color=event.color
        )
        if success:
            return {"status": "success", "message": "Event created"}
        else:
            return {"status": "error", "message": "Failed to save event"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.put("/api/v1/calendar/{event_id}")
async def update_calendar_event(event_id: str, event: CalendarEventCreate):
    """Allows the Dashboard UI to update an existing event."""
    from calendar_agent import calendar_agent
    try:
        success = calendar_agent.update_event(
            event_id=event_id,
            start_date=event.start_date,
            start_time=event.start_time,
            description=event.description,
            end_time=event.end_time,
            is_reminder=event.is_reminder,
            category=event.category,
            priority=event.priority,
            agent_id=event.agent_id,
            location=event.location,
            color=event.color
        )
        if success:
            return {"status": "success", "message": "Event updated"}
        else:
            return {"status": "error", "message": "Event not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.delete("/api/v1/calendar/{event_id}")
async def delete_calendar_event(event_id: str):
    """Allows the Dashboard UI to delete an event."""
    from calendar_agent import calendar_agent
    try:
        success = calendar_agent.delete_event(event_id)
        if success:
            return {"status": "success", "message": "Event deleted"}
        else:
            return {"status": "error", "message": "Event not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
