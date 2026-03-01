from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from sqlalchemy.orm import Session

import database
import models
from cfo import cfo

# Ensure database tables exist
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Sintari Commander API", version="0.1.0")

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

@app.get("/api/v1/memory/recent")
async def get_recent_memory():
    """Returns the simulated recent memory log for the dashboard."""
    # In a full implementation, this queries OpenSearch and PostgreSQL
    return {
        "memory_items": [
            {
                "file": "master.prompt.md",
                "category": "System Regler",
                "tokens": 4520,
                "timestamp": "Idag 14:32"
            },
            {
                "file": "api_test_results.json",
                "category": "Verifiering",
                "tokens": 842,
                "timestamp": "Idag 10:15"
            },
            {
                "file": "ceo_profile.yaml",
                "category": "Kontext",
                "tokens": 120,
                "timestamp": "Igår"
            }
        ],
        "opensearch_usage_percent": 12,
        "postgres_active_sessions": 4
    }

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
            event.start_date,
            event.start_time,
            event.description,
            event.end_time
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
            event_id,
            event.start_date,
            event.start_time,
            event.description,
            event.end_time
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
