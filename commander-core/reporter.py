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
AUTHORIZED_USER = int(os.getenv("TELEGRAM_AUTHORIZED_USER_ID", "123456789"))

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
            InlineKeyboardButton(text="🧠 Hot-Swap Model", callback_data="btn_model_swap"),
            InlineKeyboardButton(text="❤️ System Pulse", callback_data="btn_pulse"),
        ],
        [
            InlineKeyboardButton(text="🔥 Trigger Hype Pipeline", callback_data="btn_hype_job"),
            InlineKeyboardButton(text="💰 Financial Summary", callback_data="btn_cfo"),
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
        if message.from_user.id != AUTHORIZED_USER:
            await message.reply("Access Denied. You are not authorized to command me.")
            return False
        return True

    async def send_morning_briefing(self, briefing_text: str):
        """Sends the daily Morning Briefing."""
        try:
            await self.bot.send_message(
                chat_id=AUTHORIZED_USER,
                text=f"🌅 **Morning Briefing - CEO Mode**\n\n{briefing_text}",
                parse_mode="Markdown"
            )
        except Exception as e:
            logging.error(f"Failed to send morning briefing: {e}")

    async def send_alert(self, alert_text: str):
        """Sends an immediate proactive alert."""
        try:
            await self.bot.send_message(
                chat_id=AUTHORIZED_USER,
                text=f"⚠️ **PROACTIVE ALERT**\n\n{alert_text}",
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
            "Welcome Commander. I am standing by.",
            reply_markup=get_main_menu()
        )

@dp.message(Command("pulse"))
async def cmd_pulse(message: types.Message):
    if await reporter_instance.verify_user(message):
        await message.answer("❤️ Pulse: **Online and Nominal**. All systems active.")

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
# CALLBACK HANDLERS (For Inline Keyboard)
# ==========================================

@dp.callback_query()
async def callbacks_handlers(callback: types.CallbackQuery):
    if callback.from_user.id != AUTHORIZED_USER:
        await callback.answer("Access Denied", show_alert=True)
        return

    # Acknowledge the callback to remove the "loading" state on the button
    await callback.answer()

    if callback.data == "btn_model_swap":
        await callback.message.answer("Swapping models...")
    elif callback.data == "btn_pulse":
        await callback.message.answer("❤️ Heartbeat online.")
    elif callback.data == "btn_hype_job":
        await callback.message.answer("🔥 Hype pipeline queued.")
    elif callback.data == "btn_cfo":
        from cfo import cfo
        summary = cfo.get_financial_summary()
        await callback.message.answer(summary)

async def start_telegram_polling():
    """Starts the Telegram polling loop. Should be run as an asyncio task."""
    logging.info("Starting Telegram polling for The Commander...")
    await dp.start_polling(bot)
