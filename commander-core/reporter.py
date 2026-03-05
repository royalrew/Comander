import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()

# Setup logging for the Telegram bot
logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# Safely parse IDs as a list of strings
AUTHORIZED_USERS = [u.strip() for u in os.getenv("TELEGRAM_AUTHORIZED_USER_ID", "123456789").split(',')]

if not TELEGRAM_TOKEN:
    raise ValueError("CRITICAL: TELEGRAM_BOT_TOKEN environment variable is missing.")

# Initialize the Bot and Dispatcher
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Pre-defined Inline Keyboards
def get_main_menu() -> InlineKeyboardMarkup:
    """Returns the main interactive menu for CEO Mode."""
    buttons = [
        [
            InlineKeyboardButton(text="🧠 Byt AI-Modell", callback_data="btn_model_swap"),
            InlineKeyboardButton(text="❤️ Systemstatus", callback_data="btn_pulse"),
        ],
        [
            InlineKeyboardButton(text="🔥 Starta Hype-Loopen", callback_data="btn_hype_job"),
            InlineKeyboardButton(text="💰 Finansiell Översikt", callback_data="btn_cfo"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

class Reporter:
    """
    Handles communication with the CEO via Telegram.
    Includes the Morning Briefing and interactive menus.
    """
    def __init__(self, bot_instance: Bot):
        self.bot = bot_instance

    async def verify_user(self, message: types.Message) -> bool:
        """Verifies if the sender is the authorized CEO."""
        if str(message.from_user.id) not in AUTHORIZED_USERS:
            await message.reply(f"Åtkomst Nekad. Du är inte auktoriserad att ge mig order. (Ditt ID: {message.from_user.id})")
            return False
        return True

    async def send_morning_briefing(self, briefing_text: str):
        """Sends the daily Morning Briefing."""
        for user in AUTHORIZED_USERS:
            try:
                await self.bot.send_message(
                    chat_id=user,
                    text=f"🌅 **Morgonrapport - CEO Mode**\n\n{briefing_text}",
                    parse_mode="Markdown"
                )
            except Exception as e:
                logging.error(f"Failed to send morning briefing to user {user}: {e}")

    async def send_alert(self, alert_text: str):
        """Sends an immediate proactive alert."""
        for user in AUTHORIZED_USERS:
            try:
                await self.bot.send_message(
                    chat_id=user,
                    text=f"⚠️ **PROAKTIV VARNING**\n\n{alert_text}",
                    parse_mode="Markdown"
                )
            except Exception as e:
                logging.error(f"Failed to send alert to user {user}: {e}")

reporter_instance = Reporter(bot)

# ==========================================
# COMMAND HANDLERS
# ==========================================

@dp.message(Command("start", "menu"))
async def cmd_start(message: types.Message):
    if await reporter_instance.verify_user(message):
        await message.answer(
            "Välkommen Commander. Jag väntar på dina direktiv.",
            reply_markup=get_main_menu()
        )

@dp.message(Command("pulse"))
async def cmd_pulse(message: types.Message):
    if await reporter_instance.verify_user(message):
        await message.answer("❤️ Puls: **Online och Stabil**. Alla system är aktiva.")

@dp.message(Command("model"))
async def cmd_model(message: types.Message):
    if await reporter_instance.verify_user(message):
        # Placeholder for model swapping logic
        await message.answer("🔄 Swapping to alternative Cortex Model... [Feature Pending]")

@dp.message(Command("hype"))
async def cmd_hype(message: types.Message):
    if await reporter_instance.verify_user(message):
        await message.answer("🔥 Triggering manual Hype job for Real Estate presets. [Feature Pending]")

@dp.message(Command("review"))
async def cmd_review(message: types.Message):
    """Manually triggers the Mid-Week Accountability Review."""
    if await reporter_instance.verify_user(message):
        await message.answer("⚖️ Initierar Mid-Week Review. Validerar dina senaste pushade GitHub-commits mot din affärsplan...")
        import routines
        import asyncio
        # Run asynchronously as perform_midweek_review is an async function
        await routines.perform_midweek_review()

# ==========================================
# DETERMINISTIC SCHEDULE IMPORT (bypasses LLM)
# ==========================================

@dp.message(Command("schema"))
async def cmd_schema(message: types.Message):
    """Parses a pasted work schedule deterministically and bulk-inserts into the calendar.
    Usage: /schema followed by lines like '2/3 Mån: 07:00-16:00 (optional note)'
    """
    if not await reporter_instance.verify_user(message):
        return
    
    import re
    import uuid
    from database import SessionLocal
    from models import EventDB, SystemLogDB
    
    raw_text = message.text.replace("/schema", "", 1).strip()
    if not raw_text:
        await message.reply("ℹ️ Användning: /schema följt av ditt arbetsschema.\nExempel:\n/schema\n2/3 Mån: 07:00-16:00\n5/3 Tor: 08:00-15:30 (Utbildning)")
        return
    
    # Detect the year from context (default to current year)
    year_match = re.search(r'(20\d{2})', raw_text)
    year = int(year_match.group(1)) if year_match else 2026
    
    # Pattern: day/month + optional weekday + colon + time range(s) + optional note
    line_pattern = re.compile(
        r'(\d{1,2})/(\d{1,2})\s*\w*\s*:?\s*'
        r'(\d{1,2}[:\.:]\d{2})\s*[\-\–]\s*(\d{1,2}[:\.:]\d{2})'
        r'(?:\s*(?:&|och)\s*(\d{1,2}[:\.:]\d{2})\s*[\-\–]\s*(\d{1,2}[:\.:]\d{2}))?'
        r'(?:\s*\(?(.+?)\)?)?\s*$',
        re.MULTILINE
    )
    
    matches = line_pattern.findall(raw_text)
    
    if not matches:
        await message.reply("❌ Kunde inte tolka några rader. Se till att formatet är:\n`5/3 Tor: 08:00-15:30`\neller\n`15/3 Sön: 07:00-13:00 & 15:30-21:00`", parse_mode="Markdown")
        return
    
    db = SessionLocal()
    added = 0
    details = []
    
    try:
        for m in matches:
            day, month = int(m[0]), int(m[1])
            start1 = m[2].replace('.', ':')
            end1 = m[3].replace('.', ':')
            start2 = m[4].replace('.', ':') if m[4] else None
            end2 = m[5].replace('.', ':') if m[5] else None
            note = m[6].strip() if m[6] else ""
            
            date_str = f"{year}-{month:02d}-{day:02d}"
            desc = f"Jobb{' (' + note + ')' if note else ''}"
            
            # First shift
            event1 = EventDB(
                id=str(uuid.uuid4()),
                start_date=date_str,
                start_time=start1,
                end_time=end1,
                description=desc,
                category="Work",
                priority="Medium",
                agent_id="SchemaImport",
                reminder_sent=True
            )
            db.add(event1)
            added += 1
            details.append(f"{date_str} {start1}-{end1}")
            
            # Second shift (split day)
            if start2 and end2:
                event2 = EventDB(
                    id=str(uuid.uuid4()),
                    start_date=date_str,
                    start_time=start2,
                    end_time=end2,
                    description=f"Jobb (Pass 2){' - ' + note if note else ''}",
                    category="Work",
                    priority="Medium",
                    agent_id="SchemaImport",
                    reminder_sent=True
                )
                db.add(event2)
                added += 1
                details.append(f"{date_str} {start2}-{end2}")
        
        # Audit log
        audit = SystemLogDB(
            action_type="schema_import",
            details=f"Imported {added} work shifts via /schema command."
        )
        db.add(audit)
        db.commit()
        
        await message.reply(
            f"✅ **Schema importerat!**\n\n"
            f"**{added} arbetspass** har lagts till i kalendern.\n\n"
            + "\n".join([f"• {d}" for d in details[:10]])
            + (f"\n... och {len(details) - 10} till." if len(details) > 10 else ""),
            parse_mode="Markdown"
        )
    except Exception as e:
        db.rollback()
        await message.reply(f"❌ Databasfel: {str(e)}")
    finally:
        db.close()

# ==========================================
# CHAT HANDLER (Modell-Lera / Conversational Mode)
# ==========================================
user_sessions = {}

@dp.message()
async def chat_handler(message: types.Message):
    if not await reporter_instance.verify_user(message):
        return

    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Commander"
    user_text = message.text

    if not user_text:
        return

    # Show typing indicator
    await bot.send_chat_action(chat_id=user_id, action="typing")

    # Initialize memory if empty
    if user_id not in user_sessions:
        user_sessions[user_id] = []
        
    history = user_sessions[user_id]

    try:
        from router import router
        import asyncio

        def ask_ai():
            return router.ask_cortex(user_prompt=user_text, history=history, user_name=user_name)

        # Run synchronously in a thread to not block other Telegram users
        reply = await asyncio.to_thread(ask_ai)

        # Update history
        history.append({"role": "user", "content": user_text})
        history.append({"role": "assistant", "content": reply})
        
        # Keep memory bounded to last 20 messages to save context window
        user_sessions[user_id] = history[-20:]

        await message.answer(reply)
    except Exception as e:
        logging.error(f"Chat error: {e}")
        await message.answer(f"❌ Ett fel uppstod i mina kognitiva kretsar: {str(e)}")

# ==========================================
# CALLBACK HANDLERS (For Inline Keyboard)
# ==========================================

@dp.callback_query()
async def callbacks_handlers(callback: types.CallbackQuery):
    if str(callback.from_user.id) not in AUTHORIZED_USERS:
        await callback.answer("Åtkomst Nekad", show_alert=True)
        return

    # Acknowledge the callback to remove the "loading" state on the button
    await callback.answer()

    if callback.data == "btn_model_swap":
        await callback.message.answer("Byter AI-modeller...")
    elif callback.data == "btn_pulse":
        await callback.message.answer("❤️ Systempuls stabil.")
    elif callback.data == "btn_hype_job":
        await callback.message.answer("🔥 Hype-uppdrag aktiverat. Genererar multi-modala tillgångar... (Detta tar ~15 sekunder)")
        
        # Run the synchronous pipeline in a background thread so we don't block the bot
        import asyncio
        from pipeline import pipeline
        
        def run_pipeline():
            return pipeline.execute_full_run("Cyberpunk Enterprise GRC Agent")
            
        try:
            result = await asyncio.to_thread(run_pipeline)
            
            msg = (
                f"✅ **Genesis Mission Slutfört**\n\n"
                f"**Tema:** Cyberpunk Enterprise GRC Agent\n"
                f"**Länk till Bild:** [Visa på R2]({result['assets']['image']})\n\n"
                f"**Viralt Inlägg Genererat:**\n{result['caption']}\n\n"
                f"*(Sparat säkert i Minnesbanken)*"
            )
            await callback.message.answer(msg, parse_mode="Markdown", disable_web_page_preview=False)
        except Exception as e:
            await callback.message.answer(f"❌ Genesis Mission misslyckades: {str(e)}")
    elif callback.data == "btn_cfo":
        from cfo import cfo
        summary = cfo.get_financial_summary()
        await callback.message.answer(summary)

async def start_telegram_polling():
    """Starts the Telegram polling loop. Should be run as an asyncio task."""
    logging.info("Starting Telegram polling for The Commander...")
    await dp.start_polling(bot)
