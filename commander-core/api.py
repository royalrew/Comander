from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any
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
        count = memory_bank.count_memories()
    except Exception as e:
        print(f"Error checking memory count: {e}")
        
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
    """Returns the last 5 stored memories from pgvector."""
    try:
        from sqlalchemy import text as sql_text
        from database import engine
        with engine.connect() as conn:
            result = conn.execute(sql_text("""
                SELECT id, text, category, timestamp 
                FROM memories 
                ORDER BY timestamp DESC 
                LIMIT 5
            """))
            rows = result.fetchall()
            return {"memories": [{"id": str(r[0]), "text": r[1], "category": r[2], "timestamp": r[3].isoformat() if r[3] else None} for r in rows]}
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

class CalendarDaySync(BaseModel):
    date: str
    events: list[dict]

@app.put("/api/v1/calendar/sync_day")
async def sync_calendar_day(payload: CalendarDaySync):
    """Replaces all events on a specific day with the provided list of events."""
    from calendar_agent import calendar_agent
    try:
        success = calendar_agent.sync_day(payload.date, payload.events)
        if success:
            return {"status": "success", "message": f"Synced {payload.date} with {len(payload.events)} events."}
        else:
            return {"status": "error", "message": "Failed to sync calendar day."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

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

# --- MISSION CONTROL (PLANS) ENDPOINTS ---

@app.get("/api/v1/plans")
async def get_all_plans():
    """Returns all active, paused, and scheduled jobs from APScheduler."""
    from scheduler_module import commander_scheduler
    jobs = []
    
    for job in commander_scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
            "is_paused": job.next_run_time is None
        })
        
    return {"status": "success", "jobs": jobs}

@app.post("/api/v1/plans/{job_id}/pause")
async def pause_plan(job_id: str):
    """Pauses a scheduled job."""
    from scheduler_module import commander_scheduler
    job = commander_scheduler.get_job(job_id)
    if job:
        job.pause()
        return {"status": "success", "message": f"Job {job_id} paused"}
    return {"status": "error", "message": "Job not found"}

@app.post("/api/v1/plans/{job_id}/resume")
async def resume_plan(job_id: str):
    """Resumes a paused job."""
    from scheduler_module import commander_scheduler
    job = commander_scheduler.get_job(job_id)
    if job:
        job.resume()
        return {"status": "success", "message": f"Job {job_id} resumed"}
    return {"status": "error", "message": "Job not found"}

@app.post("/api/v1/plans/{job_id}/trigger")
async def trigger_plan(job_id: str):
    """Manually triggers a job to run immediately."""
    from scheduler_module import commander_scheduler
    job = commander_scheduler.get_job(job_id)
    if job:
        import asyncio
        if asyncio.iscoroutinefunction(job.func):
            asyncio.create_task(job.func(*job.args, **job.kwargs))
        else:
            asyncio.get_event_loop().run_in_executor(None, job.func, *job.args, **job.kwargs)
        return {"status": "success", "message": f"Job {job_id} triggered to run immediately"}
    return {"status": "error", "message": "Job not found"}

# --- RUNTIME ---

if __name__ == "__main__":
    import uvicorn
    # Start the server locally for testing. Port 8000 by default.
