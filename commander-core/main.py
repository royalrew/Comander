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
    """Generates and sends the daily summary via the Reporter."""
    from calendar_agent import calendar_agent
    from cfo import cfo
    from audit_module import audit_module
    
    events = calendar_agent.get_todays_events()
    
    if events:
        schema_text = "Dagens Schema (Bokat):\n" + "\n".join([f"• {e['start_time']}: {e['description']}" for e in events])
    else:
        schema_text = "Dagens Schema: (Helt rent. Du har kontrollen.)"
        
    audit_text = audit_module.generate_audit_report()
        
    briefing = f"🌅 **God morgon Commander!**\n\n• The Cortex Heartbeat: Stabil\n• Dagens API Spend: ${cfo.current_daily_spend:.2f}\n\n{schema_text}\n\n{audit_text}"
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
