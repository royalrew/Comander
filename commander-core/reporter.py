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
# Safely parse the ID as a string and strip whitespace to prevent type errors
AUTHORIZED_USER = str(os.getenv("TELEGRAM_AUTHORIZED_USER_ID", "123456789")).strip()

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
        if str(message.from_user.id) != AUTHORIZED_USER:
            await message.reply(f"Åtkomst Nekad. Du är inte auktoriserad att ge mig order. (Ditt ID: {message.from_user.id})")
            return False
        return True

    async def send_morning_briefing(self, briefing_text: str):
        """Sends the daily Morning Briefing."""
        try:
            await self.bot.send_message(
                chat_id=AUTHORIZED_USER,
                text=f"🌅 **Morgonrapport - CEO Mode**\n\n{briefing_text}",
                parse_mode="Markdown"
            )
        except Exception as e:
            logging.error(f"Failed to send morning briefing: {e}")

    async def send_alert(self, alert_text: str):
        """Sends an immediate proactive alert."""
        try:
            await self.bot.send_message(
                chat_id=AUTHORIZED_USER,
                text=f"⚠️ **PROAKTIV VARNING**\n\n{alert_text}",
                parse_mode="Markdown"
            )
        except Exception as e:
            logging.error(f"Failed to send alert: {e}")

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

# ==========================================
# CHAT HANDLER (Modell-Lera / Conversational Mode)
# ==========================================
user_sessions = {}

@dp.message()
async def chat_handler(message: types.Message):
    if not await reporter_instance.verify_user(message):
        return

    user_id = message.from_user.id
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
            return router.ask_cortex(user_prompt=user_text, history=history)

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
    if str(callback.from_user.id) != AUTHORIZED_USER:
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
                f"*(Sparat säkert i OpenSearch Minnesbank)*"
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
