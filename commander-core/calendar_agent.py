import os
import json
from datetime import datetime
from zoneinfo import ZoneInfo

# We use Swedish Time (CET/CEST) UTC+1/+2
SWEDISH_TZ = ZoneInfo("Europe/Stockholm")
CALENDAR_PATH = os.path.join(os.path.dirname(__file__), 'memory', 'calendar_db.json')

# Auto-migrate: Add missing columns if they don't exist
try:
    from database import engine
    from sqlalchemy import text
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE events ADD COLUMN category VARCHAR DEFAULT 'General'"))
        conn.execute(text("ALTER TABLE events ADD COLUMN priority VARCHAR DEFAULT 'Medium'"))
        conn.execute(text("ALTER TABLE events ADD COLUMN agent_id VARCHAR"))
        conn.execute(text("ALTER TABLE events ADD COLUMN location VARCHAR"))
        conn.execute(text("ALTER TABLE events ADD COLUMN color VARCHAR"))
        conn.execute(text("ALTER TABLE events ADD COLUMN owner VARCHAR DEFAULT 'ceo'"))
except Exception as e:
    # Columns probably already exist
    pass

class CalendarAgent:
    """Manages the Executive Calendar via the centralized PostgreSQL database."""
    
    def _load_events(self) -> list:
        from database import SessionLocal
        from models import EventDB
        db = SessionLocal()
        try:
            events = db.query(EventDB).all()
            return [{
                "id": str(e.id),
                "start_date": e.start_date,
                "start_time": e.start_time,
                "end_time": e.end_time,
                "description": e.description,
                "category": getattr(e, 'category', 'General'),
                "priority": getattr(e, 'priority', 'Medium'),
                "agent_id": getattr(e, 'agent_id', None),
                "location": getattr(e, 'location', None),
                "color": getattr(e, 'color', None),
                "owner": getattr(e, 'owner', 'ceo'),
                "created_at": e.created_at.isoformat() if getattr(e, 'created_at', None) else None,
                "is_reminder": not getattr(e, 'reminder_sent', False)
            } for e in events]
        except Exception as e:
            print(f"Error loading calendar from DB: {e}")
            return []
        finally:
            db.close()

    def get_current_time_str(self) -> str:
        """Returns the current date and time in the Swedish timezone."""
        now = datetime.now(SWEDISH_TZ)
        return now.strftime("%Y-%m-%d %H:%M:%S (%A)")

    def add_event(self, start_date: str, start_time: str, description: str, end_time: str = None, is_reminder: bool = True, category: str = "General", priority: str = "Medium", agent_id: str = None, location: str = None, color: str = None, owner: str = "ceo") -> bool:
        import uuid
        from database import SessionLocal
        from models import EventDB
        db = SessionLocal()
        try:
            event_id = str(uuid.uuid4())
            new_event = EventDB(
                id=event_id,
                start_date=start_date,
                start_time=start_time,
                end_time=end_time,
                description=description,
                category=category,
                priority=priority,
                agent_id=agent_id,
                location=location,
                color=color,
                owner=owner,
                reminder_sent=not is_reminder
            )
            db.add(new_event)
            db.commit()
            return True
        except Exception as e:
            print(f"Failed to add event: {e}")
            db.rollback()
            return False
        finally:
            db.close()

    def update_event(self, event_id: str, start_date: str, start_time: str, description: str, end_time: str = None, is_reminder: bool = True, category: str = "General", priority: str = "Medium", agent_id: str = None, location: str = None, color: str = None, owner: str = "ceo") -> bool:
        from database import SessionLocal
        from models import EventDB
        db = SessionLocal()
        try:
            event = db.query(EventDB).filter(EventDB.id == event_id).first()
            if event:
                event.start_date = start_date
                event.start_time = start_time
                event.description = description
                event.end_time = end_time
                event.category = category
                event.priority = priority
                event.agent_id = agent_id
                event.location = location
                event.color = color
                event.owner = owner
                event.reminder_sent = not is_reminder
                db.commit()
                return True
            return False
        except Exception as e:
            print(f"Failed to update event: {e}")
            db.rollback()
            return False
        finally:
            db.close()

    def delete_event(self, event_id: str) -> bool:
        """Deletes a single event by its UUID. Logs the deletion to the audit trail."""
        import logging
        logger = logging.getLogger(__name__)
        from database import SessionLocal
        from models import EventDB, SystemLogDB
        db = SessionLocal()
        try:
            event = db.query(EventDB).filter(EventDB.id == str(event_id)).first()
            if event:
                logger.warning(f"CALENDAR DELETE: Removing event '{event.description}' on {event.start_date} {event.start_time} (ID: {event_id})")
                # Audit log the deletion
                audit_entry = SystemLogDB(
                    action_type="calendar_delete",
                    details=f"Deleted: '{event.description}' on {event.start_date} {event.start_time}-{event.end_time} (ID: {event_id})"
                )
                db.add(audit_entry)
                db.delete(event)
                db.commit()
                return True
            return False
        except Exception as e:
            print(f"Failed to delete event: {e}")
            db.rollback()
            return False
        finally:
            db.close()

    def get_pending_reminders(self, current_date: str, current_time: str) -> list:
        from database import SessionLocal
        from models import EventDB
        db = SessionLocal()
        try:
            events = db.query(EventDB).filter(
                EventDB.start_date == current_date,
                EventDB.start_time == current_time,
                EventDB.reminder_sent == False
            ).all()
            
            pending = []
            for e in events:
                pending.append({"id": str(e.id), "description": e.description})
                e.reminder_sent = True # Mark as sent immediately to prevent dupes
            db.commit()
            return pending
        except Exception as e:
            print(f"Failed to get reminders: {e}")
            db.rollback()
            return []
        finally:
            db.close()

    def get_todays_events(self) -> list:
        now = datetime.now(SWEDISH_TZ)
        today_str = now.strftime("%Y-%m-%d")
        events = self._load_events()
        return [e for e in events if e.get("start_date") == today_str]

    def get_upcoming_events(self, days: int = 7) -> list:
        now = datetime.now(SWEDISH_TZ)
        events = self._load_events()
        upcoming = []
        
        for e in events:
            try:
                event_date = datetime.strptime(e["start_date"], "%Y-%m-%d").replace(tzinfo=SWEDISH_TZ)
                if 0 <= (event_date.date() - now.date()).days <= days:
                    upcoming.append(e)
            except ValueError:
                continue
                
        return upcoming

    def sync_day(self, date_str: str, events: list) -> bool:
        """Completely replaces all events on a specific date with a new list of events."""
        import uuid
        from database import SessionLocal
        from models import EventDB, SystemLogDB
        
        db = SessionLocal()
        try:
            # First, delete all existing events for this date
            db.query(EventDB).filter(EventDB.start_date == date_str).delete()
            
            # Then, insert the new events
            added_count = 0
            for evt in events:
                new_event = EventDB(
                    id=str(uuid.uuid4()),
                    start_date=date_str,
                    start_time=evt.get("start_time", "00:00"),
                    end_time=evt.get("end_time"),
                    description=evt.get("description", "Otitlad händelse"),
                    category=evt.get("category", "General"),
                    priority=evt.get("priority", "Medium"),
                    agent_id=evt.get("agent_id"),
                    location=evt.get("location"),
                    color=evt.get("color"),
                    owner="ceo",
                    reminder_sent=not evt.get("is_reminder", True)
                )
                db.add(new_event)
                added_count += 1
                
            # Log this action for AI awareness
            audit_entry = SystemLogDB(
                action_type="calendar_sync_day",
                details=f"Synced schedule for {date_str} ({added_count} events)."
            )
            db.add(audit_entry)
            
            db.commit()
            
            # Also store a memory to ensure the AI knows we manually updated the schedule
            from memory_module import memory_bank
            memory_bank.store_memory(
                category="ScheduleUpdate", 
                text=f"Användaren har manuellt planerat och sparat schemat för {date_str}. Det finns nu {added_count} händelser inlagda denna dag."
            )
            
            return True
        except Exception as e:
            print(f"Failed to sync day {date_str}: {e}")
            db.rollback()
            return False
        finally:
             db.close()

calendar_agent = CalendarAgent()
