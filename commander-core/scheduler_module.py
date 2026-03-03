from apscheduler.schedulers.asyncio import AsyncIOScheduler
from zoneinfo import ZoneInfo

commander_scheduler = AsyncIOScheduler(timezone=ZoneInfo("Europe/Stockholm"))
