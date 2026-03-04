import os
import asyncio
import logging
from dotenv import load_dotenv

from reporter import start_telegram_polling, reporter_instance
from router import router
from pipeline import pipeline

load_dotenv()

# Setup Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# The Daemon loop for proactive behavior
async def watchdog_heartbeat():
    """
    Poller that runs locally using the Watchdog model (e.g. llama3) to evaluate if 
    any proactive work is needed overnight.
    """
    logger.info("Executing Watchdog Heartbeat...")
    
    # Example logic: Read recent logs, issues, or unread messages
    # We use a mocked active state for now.
    simulated_context = "No new files modified. RAM usage 40%. All targets nominal."
    
    action_required = router.ask_watchdog(simulated_context)
    
    if action_required:
        logger.info("Watchdog detected anomaly or required work! Waking up Cortex...")
        
        cortex_decision = router.ask_cortex(
            system_prompt="You are the COO evaluating a system prompt from the watchdog. What is the next play?",
            user_prompt=f"Watchdog Context: {simulated_context}"
        )
        
        logger.info(f"Cortex decision: {cortex_decision}")
        await reporter_instance.send_alert(f"Proactive Action Initiated: {cortex_decision}")
    else:
        logger.info("Watchdog assessment: NO ACTION REQUIRED.")

async def morning_briefing_job():
    """Generates and sends the daily summary via the Health Coach persona."""
    from calendar_agent import calendar_agent
    from cfo import cfo
    from router import router
    import yaml
    
    # We dynamically import the prompt to ensure it's up to date
    from swarm.agents.health_agent import HEALTH_COACH_PROMPT
    
    events = calendar_agent.get_todays_events()
    schema_text = "Dagens Schema:"
    if events:
        schema_text += "\n" + "\n".join([f"- {e['start_time']} till {e.get('end_time', 'okänt')}: {e['description']}" for e in events])
    else:
        schema_text += " Helt rent. Inga möten inbokade."
        
    profile_data = {}
    try:
        profile_path = os.path.join(os.path.dirname(__file__), 'ceo_profile.yaml')
        with open(profile_path, 'r', encoding='utf-8') as f:
            profile_data = yaml.safe_load(f)
    except Exception as e:
        logger.warning(f"Could not load ceo_profile for morning briefing: {e}")

    work_hours = profile_data.get("preferences", {}).get("working_hours", "Unknown")
    train_constraints = profile_data.get("preferences", {}).get("training_constraints", "Unknown")
    
    prompt = f"Klockan är 07:00. Här är chefens kalender för dagen: {schema_text}\nArbetstider: {work_hours}\nTräningsrestriktioner: {train_constraints}\n\nGe honom en extremt strukturerad Battle Plan för dagen (träning, fokus och återhämtning). Lokalisera luckor i schemat och bestäm exakt NÄR han ska träna. Håll det kort, hårt och inspirerande. Ingen jävla daltande."
    
    battle_plan = await router.ask_cortex_direct_async(user_prompt=prompt, system_prompt=HEALTH_COACH_PROMPT)
    
    briefing = f"🌅 **The Morning Battle Plan**\n\n{battle_plan}\n\n_System Status: API Spend ${cfo.current_daily_spend:.2f}_"
    await reporter_instance.send_morning_briefing(briefing)

async def check_reminders_job():
    """Checks for due calendar events every minute and sends reminders."""
    from calendar_agent import calendar_agent
    from reporter import reporter_instance
    from datetime import datetime
    from zoneinfo import ZoneInfo
    
    now = datetime.now(ZoneInfo("Europe/Stockholm"))
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M")
    
    reminders = calendar_agent.get_pending_reminders(current_date, current_time)
    for r in reminders:
        await reporter_instance.send_alert(f"⏰ **Påminnelse:**\n{r['description']}")

async def github_code_review_job():
    """Reads latest commits and performs an AI code review."""
    from reporter import reporter_instance
    # TODO: Connect to actual GitHub Agent
    logger.info("Executing GitHub Code Review...")
    await reporter_instance.send_alert("🔍 **GitHub Code Review Initiated:**\nGranskar de senaste kodändringarna för potentiella buggar eller säkerhetsrisker...")

async def main():
    logger.info("Booting Commander Core (CEO Mode)...")
    
    # 1. Start the Proactive Scheduler
    from scheduler_module import commander_scheduler
    
    # Run the Watchdog Heartbeat every hour
    commander_scheduler.add_job(watchdog_heartbeat, 'interval', minutes=60, id='watchdog_heartbeat', name='Watchdog Heartbeat')
    
    # Run the Mid-Week Review on Wednesdays at 14:00
    import routines
    commander_scheduler.add_job(routines.perform_midweek_review, 'cron', day_of_week='wed', hour=14, minute=0, id='midweek_review', name='Mid-Week Review')
    
    # Run the Morning Briefing daily at 07:00
    commander_scheduler.add_job(morning_briefing_job, 'cron', hour=7, minute=0, id='morning_briefing', name='Morning Briefing')

    # Check for reminders every minute
    commander_scheduler.add_job(check_reminders_job, 'cron', minute='*', id='check_reminders', name='Calendar Reminders')
    
    # Run GitHub Code Review daily at 18:00
    commander_scheduler.add_job(github_code_review_job, 'cron', hour=18, minute=0, id='github_code_review', name='GitHub Code Review')
    
    commander_scheduler.start()
    logger.info("APScheduler Proactive Loops Started.")

    # 2. Start the API Server and Telegram polling concurrently
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    config = uvicorn.Config(app="api:app", host="0.0.0.0", port=port, loop="asyncio")
    server = uvicorn.Server(config)
    
    logger.info(f"Starting FastAPI on 0.0.0.0:{port} & Telegram Polling concurrently...")
    await asyncio.gather(
        server.serve(),
        start_telegram_polling()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Commander Core shutting down...")
