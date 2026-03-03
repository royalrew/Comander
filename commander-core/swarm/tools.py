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
