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
