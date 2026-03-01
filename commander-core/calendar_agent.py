import os
import json
from datetime import datetime
from zoneinfo import ZoneInfo

# We use Swedish Time (CET/CEST) UTC+1/+2
SWEDISH_TZ = ZoneInfo("Europe/Stockholm")
CALENDAR_PATH = os.path.join(os.path.dirname(__file__), 'memory', 'calendar_db.json')

class CalendarAgent:
    """Manages the Executive Calendar via the centralized PostgreSQL database."""
    
    def _load_events(self) -> list:
        from database import SessionLocal
        from models import EventDB
        db = SessionLocal()
        try:
            events = db.query(EventDB).order_by(EventDB.start_date.asc(), EventDB.start_time.asc()).all()
            return [
                {
                    "id": str(e.id),
                    "start_date": e.start_date,
                    "start_time": e.start_time,
                    "end_time": e.end_time,
                    "description": e.description,
                    "created_at": e.created_at.strftime("%Y-%m-%d %H:%M:%S") if e.created_at else ""
                }
                for e in events
            ]
        except Exception as e:
            print(f"Error loading calendar from DB: {e}")
            return []
        finally:
            db.close()

    def get_current_time_str(self) -> str:
        """Returns the current date and time in the Swedish timezone."""
        now = datetime.now(SWEDISH_TZ)
        return now.strftime("%Y-%m-%d %H:%M:%S (%A)")

    def add_event(self, start_date: str, start_time: str, description: str, end_time: str = None) -> bool:
        import uuid
        from database import SessionLocal
        from models import EventDB
        db = SessionLocal()
        try:
            new_event = EventDB(
                id=str(uuid.uuid4()),
                start_date=start_date,
                start_time=start_time,
                end_time=end_time,
                description=description
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

    def update_event(self, event_id: str, start_date: str, start_time: str, description: str, end_time: str = None) -> bool:
        from database import SessionLocal
        from models import EventDB
        db = SessionLocal()
        try:
            event = db.query(EventDB).filter(EventDB.id == str(event_id)).first()
            if event:
                event.start_date = start_date
                event.start_time = start_time
                event.end_time = end_time
                event.description = description
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
        from database import SessionLocal
        from models import EventDB
        db = SessionLocal()
        try:
            event = db.query(EventDB).filter(EventDB.id == str(event_id)).first()
            if event:
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

calendar_agent = CalendarAgent()
