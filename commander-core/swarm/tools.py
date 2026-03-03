from langchain_core.tools import tool

@tool
def memorize_fact(fact: str, category: str = "General") -> str:
    """Saves an important fact about the user, project, or context to Long-Term Persistent Memory (OpenSearch).
    Använd detta för att permanent spara mål, preferenser och information om CEO:n."""
    try:
        from memory_module import memory_bank
        success, err_msg = memory_bank.store_memory(category, fact)
        if success:
            return f"Success: Minnet är lagrat permanent i OpenSearch. ('{fact}')"
        else:
            return f"Error: Failed to store memory. Reason: {err_msg}"
    except Exception as e:
        return f"System Error: {str(e)}"

@tool
def recall_memories(query: str, limit: int = 5) -> str:
    """Söker i Vector Databasen (OpenSearch) efter tidigare sparad kontext (Minnen).
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
    Används när du (din agent-roll) vill boka, ändra eller ta bort något i CEO:ns kalender. Sätt ditt agent_namn i 'agent_id' (t.ex. 'HealthCoach')."""
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
