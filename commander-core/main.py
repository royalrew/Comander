import os
import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
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
    
    events = calendar_agent.get_todays_events()
    
    if events:
        schema_text = "Dagens Schema (Bokat):\n" + "\n".join([f"• {e['start_time']}: {e['description']}" for e in events])
    else:
        schema_text = "Dagens Schema: (Helt rent. Du har kontrollen.)"
        
    briefing = f"🌅 **God morgon Commander!**\n\n• The Cortex Heartbeat: Stabil\n• Dagens API Spend: ${cfo.current_daily_spend:.2f}\n\n{schema_text}"
    await reporter_instance.send_morning_briefing(briefing)

async def main():
    logger.info("Booting Commander Core (CEO Mode)...")
    
    # 1. Start the Proactive Scheduler
    scheduler = AsyncIOScheduler()
    
    # Run the Watchdog Heartbeat every hour
    scheduler.add_job(watchdog_heartbeat, 'interval', minutes=60)
    
    # Run the Morning Briefing daily at 07:00
    scheduler.add_job(morning_briefing_job, 'cron', hour=7, minute=0)
    
    scheduler.start()
    logger.info("APScheduler Proactive Loops Started.")

    # 2. Start the API Server and Telegram polling concurrently
    import uvicorn
    config = uvicorn.Config(app="api:app", host="127.0.0.1", port=8000, loop="asyncio")
    server = uvicorn.Server(config)
    
    logger.info("Starting FastAPI & Telegram Polling concurrently...")
    await asyncio.gather(
        server.serve(),
        start_telegram_polling()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Commander Core shutting down...")
