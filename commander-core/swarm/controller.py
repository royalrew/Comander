import os
import yaml
import logging
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from swarm.graph import swarm_engine
from audit_module import audit_module

logger = logging.getLogger("Tänkaren")
llm = ChatOpenAI(model=os.getenv("CORTEX_MODEL", "gpt-4o"), temperature=0.5)

CONTROLLER_PROMPT = """You are "Tänkaren" (The Proactive Controller) of the Sintari Enterprise system.
Your goal is to autonomously analyze the CEO's long-term goals and their recent activity, and then deduce exactly ONE clear research task that would benefit them right now. 

RULES:
1. Base your deduction purely on the CEO Profile and the recent activity log provided.
2. If they are working on a specific tech stack or business problem, your task should be finding the latest best practices, pricing, or tools for that exact problem.
3. Output ONLY the explicit string prompt that will be sent to the ResearchAgent (Utföraren). Do not include any pleasantries or reasoning. 
Example Output: "Sök nätet och skrapa den senaste officiella dokumentationen för Stripe Connect webhook hantering i Next.js 15."
"""

class ProactiveController:
    """
    The Proactive Brain of Sintari.
    Wakes up (e.g., nightly), analyzes goals vs reality, and spawns autonomous tasks.
    """
    def __init__(self):
        # Setup paths assuming this runs inside `swarm/controller.py` (two levels deep)
        self.profile_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'ceo_profile.yaml')

    def get_ceo_context(self) -> str:
        """Reads the ceo_profile.yaml for long-term goals."""
        try:
            with open(self.profile_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                goals = data.get("identity", {}).get("ultimate_goal", "")
                focus = data.get("identity", {}).get("current_business_focus", "")
                return f"Ultimate Goals: {goals}\nCurrent Focus: {focus}"
        except Exception as e:
            logger.error(f"Controller could not load ceo_profile: {e}")
            return "No profile found."

    def get_recent_activity(self) -> str:
        """Reads recent github commits or system logs to see what the CEO is actually doing."""
        return audit_module.get_recent_activity(hours=24)

    async def deduce_next_task(self) -> str:
        """Uses Cortex to deduce the next logical research step without human prompt."""
        ceo_context = self.get_ceo_context()
        activity = self.get_recent_activity()

        knowledge_payload = f"CEO PROFILE:\n{ceo_context}\n\nRECENT 24H ACTIVITY:\n{activity}"
        
        messages = [
            SystemMessage(content=CONTROLLER_PROMPT),
            HumanMessage(content=knowledge_payload)
        ]
        
        logger.info("Tänkaren: Dedukterar nästa proaktiva uppgift...")
        response = await llm.ainvoke(messages)
        task = response.content.strip()
        logger.info(f"Tänkaren beslutade: {task}")
        return task

    async def execute_nightly_routine(self):
        """
        The main autonomous loop.
        1. Deduce task.
        2. Spawn ResearchAgent.
        3. Save findings (handled by ResearchAgent via memorize_fact).
        """
        logger.info("--- NIGHTLY AUTONOMOUS ROUTINE STARTED ---")
        
        # 1. Deduce what we need to learn
        proactive_task = await self.deduce_next_task()
        
        # 2. Spawn the ResearchAgent (Utföraren)
        # We manually inject into the LangGraph state
        initial_state = {
            "messages": [HumanMessage(content=f"PROAKTIVT UPPDRAG FRÅN CONTROLLern: {proactive_task}")],
            "next_step": "ResearchAgent", # Bypass the Supervisor directly to the Executor
            "session_user_id": "System_Controller",
            "session_time": datetime.utcnow().isoformat(),
            "active_dashboard_tab": "tech",
            "dashboard_data": {}
        }
        
        logger.info("Utföraren (Clawbot) kallas in...")
        
        try:
            final_state = await swarm_engine.ainvoke(initial_state)
            
            # Extract the final answer
            messages = final_state.get("messages", [])
            final_report = messages[-1].content if messages else "Inget resultat."
            
            # Log it in the audit system
            from models import SystemLogDB
            from database import SessionLocal
            db = SessionLocal()
            try:
                db.add(SystemLogDB(
                    action_type="autonomous_nightly_research",
                    details=f"Task: {proactive_task}\nResult snippet: {final_report[:200]}..."
                ))
                db.commit()
            except Exception as db_e:
                logger.error(f"Database error in Controller: {db_e}")
            finally:
                db.close()
                
            logger.info("--- NIGHTLY AUTONOMOUS ROUTINE COMPLETED ---")
            return {
                "task": proactive_task,
                "report": final_report
            }
            
        except Exception as e:
            logger.error(f"Nightly routine failed during execution: {e}")
            return None

controller_engine = ProactiveController()
