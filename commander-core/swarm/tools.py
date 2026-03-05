from langchain_core.tools import tool

@tool
def memorize_fact(fact: str, category: str = "General") -> str:
    """Saves an important fact about the user, project, or context to Long-Term Persistent Memory (PostgreSQL pgvector).
    Använd detta för att permanent spara mål, preferenser och information om CEO:n."""
    try:
        from memory_module import memory_bank
        success, err_msg = memory_bank.store_memory(category, fact)
        if success:
            return f"Success: Minnet är lagrat permanent i Minnesbanken. ('{fact}')"
        else:
            return f"Error: Failed to store memory. Reason: {err_msg}"
    except Exception as e:
        return f"System Error: {str(e)}"

@tool
def recall_memories(query: str, limit: int = 5) -> str:
    """Söker i Minnesbanken (pgvector) efter tidigare sparad kontext (Minnen).
    Använd detta för att komma ihåg fakta relaterat till användaren, tex 'vad heter jag?', 'vilket gym tränar jag på?'.
    Anger strängen du vill söka efter."""
    try:
        from memory_module import memory_bank
        results = memory_bank.search_memory(query, limit=limit)
        if not results:
            return "Inga relevanta minnen hittades."
        
        # Format the output clearly
        formatted = "Funna minnen:\n"
        for i, hit in enumerate(results):
            text = hit.get("text", "")
            cat = hit.get("category", "")
            formatted += f"- ({cat}): {text}\n"
            
        return formatted
    except Exception as e:
        return f"System Error: {str(e)}"

@tool
def manage_calendar_event(action: str, start_date: str, start_time: str, description: str, end_time: str = None, event_id: str = None, category: str = "General", priority: str = "Medium", agent_id: str = None, location: str = None, color: str = None, is_reminder: bool = True) -> str:
    """Hantera inlägg i Executive Calendar.
    - action: "add", "update", eller "delete".
    - start_date: ÅÅÅÅ-MM-DD
    - start_time: HH:MM
    - event_id: Krävs vid "update" och "delete".
    Används när du (din agent-roll) vill boka, ändra eller ta bort något i CEO:ns kalender. Sätt ditt agent_namn i 'agent_id' (t.ex. 'HealthCoach').
    
    KRITISK SÄKERHETSREGEL FÖR DELETE:
    - Du får ALDRIG radera events utan att CEO:n EXPLICIT sagt åt dig att radera just det specifika eventet.
    - Du får ALDRIG radera flera events i rad (bulk-delete). Max 1 delete per konversation utan bekräftelse.
    - Om du är osäker, FRÅGA användaren innan du raderar."""
    try:
        from calendar_agent import calendar_agent
        if action == "add":
            success = calendar_agent.add_event(start_date, start_time, description, end_time, is_reminder, category, priority, agent_id, location, color)
            return "Event added successfully." if success else "Failed to add event."
        elif action == "update" and event_id:
            success = calendar_agent.update_event(event_id, start_date, start_time, description, end_time, is_reminder, category, priority, agent_id, location, color)
            return "Event updated successfully." if success else "Failed to update event (not found)."
        elif action == "delete" and event_id:
            success = calendar_agent.delete_event(event_id)
            return "Event deleted successfully." if success else "Failed to delete event."
        else:
            return "Invalid action or missing event_id."
    except Exception as e:
        return f"System Error: {str(e)}"

@tool
def bulk_add_calendar_events(events_json: str) -> str:
    """Lägg till FLERA kalenderevent på en gång i en enda transaktion.
    Använd detta NÄR CEO:n ger dig ett helt arbetsschema, träningsprogram, eller fler än 3 events att lägga in.
    
    Input: En JSON-sträng med en lista av event-objekt.
    Varje objekt MÅSTE ha: start_date (YYYY-MM-DD), start_time (HH:MM), description.
    Varje objekt KAN ha: end_time, category, priority, agent_id, location, color, is_reminder.
    
    Exempel:
    [{"start_date": "2026-03-05", "start_time": "07:00", "end_time": "16:00", "description": "Jobb", "category": "Work"},
     {"start_date": "2026-03-06", "start_time": "08:00", "end_time": "15:30", "description": "Utbildning Mariestad", "category": "Work", "location": "Mariestad"}]
    
    VIKTIGT: Använd ALLTID detta verktyg istället för att anropa manage_calendar_event i en loop när det är fler än 3 events."""
    import json as json_module
    import uuid
    try:
        events_list = json_module.loads(events_json)
        if not isinstance(events_list, list):
            return "Error: Input must be a JSON array of event objects."
        
        from database import SessionLocal
        from models import EventDB, SystemLogDB
        db = SessionLocal()
        
        added_count = 0
        errors = []
        try:
            for evt in events_list:
                if not evt.get("start_date") or not evt.get("start_time") or not evt.get("description"):
                    errors.append(f"Skipped invalid event: {evt}")
                    continue
                
                new_event = EventDB(
                    id=str(uuid.uuid4()),
                    start_date=evt["start_date"],
                    start_time=evt["start_time"],
                    end_time=evt.get("end_time"),
                    description=evt["description"],
                    category=evt.get("category", "General"),
                    priority=evt.get("priority", "Medium"),
                    agent_id=evt.get("agent_id", "Commander"),
                    location=evt.get("location"),
                    color=evt.get("color"),
                    reminder_sent=not evt.get("is_reminder", True)
                )
                db.add(new_event)
                added_count += 1
            
            # Audit log
            audit = SystemLogDB(
                action_type="calendar_bulk_add",
                details=f"Bulk added {added_count} events to the calendar."
            )
            db.add(audit)
            db.commit()
            
            result = f"SUCCESS: {added_count} events har lagts till i kalendern."
            if errors:
                result += f" ({len(errors)} skippade p.g.a. felaktigt format)"
            return result
        except Exception as e:
            db.rollback()
            return f"Database Error: {str(e)}"
        finally:
            db.close()
    except json_module.JSONDecodeError as e:
        return f"JSON Parse Error: {str(e)}. Make sure the input is valid JSON."

@tool
def get_calendar_view(days_ahead: int = 7) -> str:
    """Hämtar chefens kommande kalenderhändelser.
    Använd detta för att förstå hur veckan ser ut (t.ex. för att hitta en ledig lucka för träning eller ett möte).
    Returnerar en lista med händelser i textformat."""
    try:
        from calendar_agent import calendar_agent
        events = calendar_agent.get_upcoming_events(days=days_ahead)
        if not events:
            return "Kalendern är helt tom de kommande dagarna."
        
        formatted = f"Kommande händelser (nästa {days_ahead} dagarna):\n"
        for e in events:
            formatted += f"- {e['start_date']} kl {e['start_time']}: {e['description']} (ID: {e['id']})\n"
        return formatted
    except Exception as e:
        return f"System Error: {str(e)}"
