import os
import json
import uuid
import database
import models
from sqlalchemy.orm import Session

CALENDAR_PATH = os.path.join(os.path.dirname(__file__), 'memory', 'calendar_db.json')

def run_migration():
    print("Initializing Database tables...")
    models.Base.metadata.create_all(bind=database.engine)
    
    if not os.path.exists(CALENDAR_PATH):
        print("No legacy calendar_db.json found. Migration complete.")
        return

    print("Reading legacy memory...")
    try:
        with open(CALENDAR_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            events = data.get("events", [])
    except Exception as e:
        print(f"Error reading JSON: {e}")
        return

    if not events:
        print("No events to migrate.")
        return

    print(f"Migrating {len(events)} events to PostgreSQL...")
    db = database.SessionLocal()
    try:
        for evt in events:
            # Check if event already exists to prevent duplicates if script is run twice
            existing = db.query(models.EventDB).filter(
                models.EventDB.start_date == evt.get("start_date"),
                models.EventDB.start_time == evt.get("start_time"),
                models.EventDB.description == evt.get("description")
            ).first()
            
            if not existing:
                new_event = models.EventDB(
                    id=str(uuid.uuid4()),
                    start_date=evt.get("start_date"),
                    start_time=evt.get("start_time"),
                    end_time=evt.get("end_time"),
                    description=evt.get("description")
                )
                db.add(new_event)
        
        db.commit()
        print("Migration complete! You can now safely delete calendar_db.json")
    except Exception as e:
        db.rollback()
        print(f"Migration failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_migration()
