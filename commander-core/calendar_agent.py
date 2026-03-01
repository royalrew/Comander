import os
import json
from datetime import datetime
from zoneinfo import ZoneInfo

# We use Swedish Time (CET/CEST) UTC+1/+2
SWEDISH_TZ = ZoneInfo("Europe/Stockholm")
CALENDAR_PATH = os.path.join(os.path.dirname(__file__), 'memory', 'calendar_db.json')

class CalendarAgent:
    """Manages the Executive Calendar via a lightweight JSON database."""
    
    def __init__(self):
        self._ensure_db()

    def _ensure_db(self):
        """Creates the memory folder and calendar_db.json if they do not exist."""
        os.makedirs(os.path.dirname(CALENDAR_PATH), exist_ok=True)
        if not os.path.exists(CALENDAR_PATH):
            with open(CALENDAR_PATH, 'w', encoding='utf-8') as f:
                json.dump({"events": []}, f, indent=4)

    def _load_events(self) -> list:
        try:
            with open(CALENDAR_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("events", [])
        except Exception as e:
            print(f"Error loading calendar: {e}")
            return []

    def _save_events(self, events: list):
        with open(CALENDAR_PATH, 'w', encoding='utf-8') as f:
            json.dump({"events": events}, f, indent=4, ensure_ascii=False)

    def get_current_time_str(self) -> str:
        """Returns the current date and time in the Swedish timezone."""
        now = datetime.now(SWEDISH_TZ)
        return now.strftime("%Y-%m-%d %H:%M:%S (%A)")

    def add_event(self, start_date: str, start_time: str, description: str, end_time: str = None) -> bool:
        """
        Adds a new event to the calendar.
        start_date format: YYYY-MM-DD
        start_time/end_time format: HH:MM
        """
        import uuid
        events = self._load_events()
        new_event = {
            "id": str(uuid.uuid4()),
            "start_date": start_date,
            "start_time": start_time,
            "end_time": end_time,
            "description": description,
            "created_at": self.get_current_time_str()
        }
        events.append(new_event)
        
        # Sort events by date and time
        events.sort(key=lambda x: f"{x['start_date']}T{x['start_time']}")
        
        self._save_events(events)
        return True

    def update_event(self, event_id: str, start_date: str, start_time: str, description: str, end_time: str = None) -> bool:
        events = self._load_events()
        for i, e in enumerate(events):
            if str(e.get("id")) == str(event_id):
                events[i].update({
                    "start_date": start_date,
                    "start_time": start_time,
                    "end_time": end_time,
                    "description": description
                })
                events.sort(key=lambda x: f"{x['start_date']}T{x['start_time']}")
                self._save_events(events)
                return True
        return False

    def delete_event(self, event_id: str) -> bool:
        events = self._load_events()
        original_length = len(events)
        events = [e for e in events if str(e.get("id")) != str(event_id)]
        
        if len(events) < original_length:
            self._save_events(events)
            return True
        return False

    def get_todays_events(self) -> list:
        """Returns all events for the current day."""
        now = datetime.now(SWEDISH_TZ)
        today_str = now.strftime("%Y-%m-%d")
        
        events = self._load_events()
        return [e for e in events if e.get("start_date") == today_str]

    def get_upcoming_events(self, days: int = 7) -> list:
        """Returns events for the next X days."""
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
