import os
import asyncio
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from langchain_core.messages import HumanMessage
from swarm.graph import swarm_engine

api_router = APIRouter()

class AskRequest(BaseModel):
    query: str
    user_id: str = "Jimmy"

class AskResponse(BaseModel):
    response_text: str
    dashboard_update: Optional[Dict[str, Any]] = None
    active_agent: str = "Commander"

@api_router.post("/ask", response_model=AskResponse)
async def ask_endpoint(request: AskRequest):
    """
    Huvud-endpointen för Next.js Dashboard.
    All trafik går in i LangGraph-svärmen.
    """
    try:
        initial_state = {
            "messages": [HumanMessage(content=request.query)],
            "active_dashboard_tab": "overview",
            "dashboard_data": {},
            "next_step": None
        }

        final_state = await swarm_engine.ainvoke(initial_state)

        last_message = final_state["messages"][-1]
        response_text = last_message.content

        dashboard_data = final_state.get("dashboard_data", {})
        active_tab = final_state.get("active_dashboard_tab", "overview")

        return AskResponse(
            response_text=response_text,
            dashboard_update={
                "tab": active_tab,
                "data": dashboard_data
            },
            active_agent=active_tab
        )

    except Exception as e:
        print(f"🔥 SWARM ERROR (API): {e}")
        raise HTTPException(status_code=500, detail=str(e))

class ModelOrchestrator:
    """
    The hybrid bridge holding legacy internal Python calls
    while forwarding all core logic to LangGraph.
    """
    async def ask_cortex_async(self, user_prompt: str, history: list = None, system_prompt: str = None, user_name: str = "Commander") -> str:
        """
        The new async gateway for internal Telegram/Cron jobs to reach the Swarm.
        """
        try:
            langchain_messages = []
            if history:
                from langchain_core.messages import AIMessage
                for msg in history:
                    if msg.get("role") == "user":
                        langchain_messages.append(HumanMessage(content=msg.get("content", "")))
                    elif msg.get("role") == "assistant":
                        langchain_messages.append(AIMessage(content=msg.get("content", "")))
                        
            langchain_messages.append(HumanMessage(content=user_prompt))

            from datetime import datetime
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M")

            initial_state = {
                "messages": langchain_messages,
                "active_dashboard_tab": "overview",
                "dashboard_data": {},
                "next_step": None,
                "session_user_id": user_name,
                "session_time": current_time,
                "error": ""
            }

            final_state = await swarm_engine.ainvoke(initial_state)
            last_message = final_state["messages"][-1]
            return last_message.content
        except Exception as e:
            print(f"🔥 SWARM ERROR (Internal): {e}")
            return f"System Error i Svärmen: {e}"

    def ask_cortex(self, user_prompt: str, history: list = None, system_prompt: str = None, user_name: str = "Commander") -> str:
        """Fallback synchronous wrapper for legacy cron jobs if needed."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.ask_cortex_async(user_prompt, history, system_prompt, user_name))
            
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return pool.submit(asyncio.run, self.ask_cortex_async(user_prompt, history, system_prompt, user_name)).result()

    def ask_watchdog(self, context_to_evaluate: str) -> bool:
        """
        Uses the local Watchdog model (e.g. Ollama) directly.
        Bypasses the swarm since it's just a binary heartbeat check.
        """
        from litellm import completion
        watchdog_model = os.getenv("WATCHDOG_MODEL", "gpt-4o") # fallback to 4o if ollama not active
        system_prompt = "You are a watchdog evaluating system state. Reply EXPLICITLY with 'YES' if action is required, or 'NO' if nominal."
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": context_to_evaluate}
        ]
        try:
            response = completion(model=watchdog_model, messages=messages, temperature=0.1)
            return "YES" in response.choices[0].message.content.upper()
        except Exception as e:
            print(f"Watchdog error: {e}")
            return False

router = ModelOrchestrator()
