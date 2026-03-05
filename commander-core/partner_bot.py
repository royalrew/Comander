"""
Sintari Partner Bot - Hannis personliga assistent.

En vänlig, flerspråkig (Svenska/Somaliska) Telegram-bot som hjälper Hanni med:
- Att lägga in sitt arbetsschema.
- Att fråga när Jimmy jobbar.
- Att skicka påminnelser till Jimmy (och ta emot påminnelser).
- Gemensam inköpslista.

SÄKERHET: Denna bot har INTE tillgång till finansiella rapporter, GitHub, Hype Engine
eller andra känsliga Commander-verktyg.
"""

import os
import re
import uuid
import asyncio
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PartnerBot")

SWEDISH_TZ = ZoneInfo("Europe/Stockholm")

PARTNER_TOKEN = os.getenv("TELEGRAM_PARTNER_BOT_TOKEN")
PARTNER_USER_ID = os.getenv("TELEGRAM_PARTNER_USER_ID", "")
CEO_USER_ID = os.getenv("TELEGRAM_AUTHORIZED_USER_ID", "")

if not PARTNER_TOKEN:
    raise ValueError("CRITICAL: TELEGRAM_PARTNER_BOT_TOKEN environment variable is missing.")

partner_bot = Bot(token=PARTNER_TOKEN)
partner_dp = Dispatcher()

# ==========================================
# PERSONA & SYSTEM PROMPT
# ==========================================

PARTNER_SYSTEM_PROMPT = """Du är Sintari, Hannis personliga AI-assistent. Du är varm, vänlig och hjälpsam.
Du pratar ALLTID på det språk Hanni skriver till dig på (svenska eller somaliska).
Om hon skriver på somaliska, svara på somaliska. Om hon skriver på svenska, svara på svenska.

Hanni är gift med Jimmy. De bor i Töreboda, Sverige.

Dina huvuduppgifter:
1. Hjälpa Hanni att lägga in sitt arbetsschema i kalendern.
2. Berätta för henne när Jimmy jobbar (du har tillgång till hans kalender).
3. Skicka påminnelser till Jimmy (t.ex. "Påminn Jimmy att hämta barnen").
4. Hantera en gemensam inköpslista för hushållet.

VIKTIGA REGLER:
- Var alltid trevlig och använd emojis 😊
- Om Hanni säger något som "jag jobbar 8 till 17 imorgon", förstå att hon vill lägga in det i sin kalender.
- Om hon frågar "hur jobbar Jimmy?", slå upp hans kalenderhändelser.
- Om hon vill påminna Jimmy om något, skapa en påminnelse i HIS kalender.
- ALLA påminnelser du skapar åt Jimmy ska vara på SVENSKA, oavsett vilket språk Hanni pratar med dig.

PROAKTIV GUIDNING (visa i slutet av dina svar de första gångerna):
💡 Tips: Du kan skriva saker som:
• "När jobbar Jimmy idag?"
• "Jag jobbar 7 till 15 på fredag"
• "Påminn Jimmy att hämta barnen kl 16"
• "Vi behöver köpa mjölk"
• "Vad ska handlas?"
"""


# ==========================================
# AUTHORIZATION
# ==========================================

async def verify_partner(message: types.Message) -> bool:
    """Verifies if the sender is the authorized partner (Hanni)."""
    if PARTNER_USER_ID and str(message.from_user.id) != PARTNER_USER_ID:
        await message.reply(
            f"⛔ Åtkomst nekad. Denna bot är reserverad för Hanni. "
            f"(Ditt ID: {message.from_user.id})"
        )
        return False
    return True


# ==========================================
# HELPER: Get CEO's schedule for today/upcoming
# ==========================================

def get_jimmy_schedule(days_ahead: int = 1) -> str:
    """Fetches Jimmy's calendar events for today or upcoming days."""
    from calendar_agent import calendar_agent
    now = datetime.now(SWEDISH_TZ)

    if days_ahead <= 1:
        events = calendar_agent.get_todays_events()
        events = [e for e in events if e.get("owner", "ceo") == "ceo"]
        if not events:
            return "Jimmy har inga inbokade händelser idag. Han verkar vara ledig! 🎉"
        result = "📅 **Jimmys schema idag:**\n"
        for e in sorted(events, key=lambda x: x.get("start_time", "")):
            end = f"-{e['end_time']}" if e.get('end_time') else ""
            result += f"• {e['start_time']}{end}: {e['description']}\n"
        return result
    else:
        events = calendar_agent.get_upcoming_events(days=days_ahead)
        events = [e for e in events if e.get("owner", "ceo") == "ceo"]
        if not events:
            return f"Jimmy har inga inbokade händelser de närmaste {days_ahead} dagarna."
        result = f"📅 **Jimmys schema (kommande {days_ahead} dagar):**\n"
        for e in sorted(events, key=lambda x: (x.get("start_date", ""), x.get("start_time", ""))):
            end = f"-{e['end_time']}" if e.get('end_time') else ""
            result += f"• {e['start_date']} kl {e['start_time']}{end}: {e['description']}\n"
        return result


def get_hanni_schedule(days_ahead: int = 1) -> str:
    """Fetches Hanni's own calendar events."""
    from calendar_agent import calendar_agent
    now = datetime.now(SWEDISH_TZ)

    if days_ahead <= 1:
        events = calendar_agent.get_todays_events()
        events = [e for e in events if e.get("owner") == "partner"]
        if not events:
            return "Du har inga inbokade händelser idag. 🌸"
        result = "📅 **Ditt schema idag:**\n"
        for e in sorted(events, key=lambda x: x.get("start_time", "")):
            end = f"-{e['end_time']}" if e.get('end_time') else ""
            result += f"• {e['start_time']}{end}: {e['description']}\n"
        return result
    else:
        events = calendar_agent.get_upcoming_events(days=days_ahead)
        events = [e for e in events if e.get("owner") == "partner"]
        if not events:
            return f"Du har inga inbokade händelser de närmaste {days_ahead} dagarna."
        result = f"📅 **Ditt schema (kommande {days_ahead} dagar):**\n"
        for e in sorted(events, key=lambda x: (x.get("start_date", ""), x.get("start_time", ""))):
            end = f"-{e['end_time']}" if e.get('end_time') else ""
            result += f"• {e['start_date']} kl {e['start_time']}{end}: {e['description']}\n"
        return result


# ==========================================
# HELPER: Parse natural language work schedule
# ==========================================

def parse_work_schedule(text: str) -> list:
    """Parses natural language work schedule input from Hanni.

    Supports formats like:
    - 'Jag jobbar 8 till 17 imorgon'
    - '5/3 Ons: 07:00-16:00'
    - 'Jag jobbar 07-15 på fredag'

    Returns:
        list: A list of dicts with start_date, start_time, end_time, description.
    """
    now = datetime.now(SWEDISH_TZ)
    results = []

    # Pattern 1: Formal schedule lines like "5/3 Ons: 07:00-16:00"
    formal_pattern = re.compile(
        r'(\d{1,2})/(\d{1,2})\s*\w*\s*:?\s*'
        r'(\d{1,2}[:\.]?\d{0,2})\s*[\-\–]\s*(\d{1,2}[:\.]?\d{0,2})'
        r'(?:\s*(?:&|och)\s*(\d{1,2}[:\.]?\d{0,2})\s*[\-\–]\s*(\d{1,2}[:\.]?\d{0,2}))?'
        r'(?:\s*\((.+?)\))?',
        re.MULTILINE
    )

    formal_matches = formal_pattern.findall(text)
    if formal_matches:
        year = now.year
        for m in formal_matches:
            day, month = int(m[0]), int(m[1])
            start = _normalize_time(m[2])
            end = _normalize_time(m[3])
            note = m[6].strip() if m[6] else ""
            date_str = f"{year}-{month:02d}-{day:02d}"
            desc = f"Jobb{' (' + note + ')' if note else ''}"

            results.append({
                "start_date": date_str,
                "start_time": start,
                "end_time": end,
                "description": desc,
            })

            # Second shift if present
            if m[4] and m[5]:
                start2 = _normalize_time(m[4])
                end2 = _normalize_time(m[5])
                results.append({
                    "start_date": date_str,
                    "start_time": start2,
                    "end_time": end2,
                    "description": f"Jobb (Pass 2){' - ' + note if note else ''}",
                })
        return results

    # Pattern 2: Natural language like "jag jobbar 8 till 17 imorgon"
    natural_pattern = re.compile(
        r'(?:jobbar|arbetar|jobb)\s+(?:kl\s*)?(\d{1,2}(?:[:\.]?\d{0,2})?)\s*'
        r'(?:till|to|-|–)\s*(\d{1,2}(?:[:\.]?\d{0,2})?)',
        re.IGNORECASE
    )
    nat_match = natural_pattern.search(text)

    if nat_match:
        start = _normalize_time(nat_match.group(1))
        end = _normalize_time(nat_match.group(2))

        # Determine the date
        text_lower = text.lower()
        if "imorgon" in text_lower or "berri" in text_lower:
            from datetime import timedelta
            target = now + timedelta(days=1)
        elif "idag" in text_lower or "maanta" in text_lower:
            target = now
        elif "måndag" in text_lower or "isniin" in text_lower:
            target = _next_weekday(now, 0)
        elif "tisdag" in text_lower or "talaado" in text_lower:
            target = _next_weekday(now, 1)
        elif "onsdag" in text_lower or "arbaco" in text_lower:
            target = _next_weekday(now, 2)
        elif "torsdag" in text_lower or "khamiis" in text_lower:
            target = _next_weekday(now, 3)
        elif "fredag" in text_lower or "jimce" in text_lower:
            target = _next_weekday(now, 4)
        elif "lördag" in text_lower or "sabti" in text_lower:
            target = _next_weekday(now, 5)
        elif "söndag" in text_lower or "axad" in text_lower:
            target = _next_weekday(now, 6)
        else:
            # Default to tomorrow if no day is specified
            from datetime import timedelta
            target = now + timedelta(days=1)

        date_str = target.strftime("%Y-%m-%d")
        results.append({
            "start_date": date_str,
            "start_time": start,
            "end_time": end,
            "description": "Jobb",
        })

    return results


def _normalize_time(t: str) -> str:
    """Converts '8' -> '08:00', '15.30' -> '15:30', '07:00' -> '07:00'."""
    t = t.strip().replace(".", ":")
    if ":" not in t:
        t = f"{int(t):02d}:00"
    parts = t.split(":")
    return f"{int(parts[0]):02d}:{parts[1] if len(parts) > 1 and parts[1] else '00'}"


def _next_weekday(dt: datetime, weekday: int) -> datetime:
    """Returns the next occurrence of the given weekday (0=Mon, 6=Sun)."""
    from datetime import timedelta
    days_ahead = weekday - dt.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return dt + timedelta(days=days_ahead)


# ==========================================
# HELPER: Household Shopping List (Cross-Memory)
# ==========================================

def get_shopping_list() -> list:
    """Reads the current household shopping list from the database."""
    from database import SessionLocal
    from models import SettingDB
    import json

    db = SessionLocal()
    try:
        setting = db.query(SettingDB).filter(SettingDB.key == "household_shopping_list").first()
        if setting and setting.value:
            return json.loads(setting.value)
        return []
    except Exception:
        return []
    finally:
        db.close()


def save_shopping_list(items: list) -> bool:
    """Saves the household shopping list to the database."""
    from database import SessionLocal
    from models import SettingDB
    import json

    db = SessionLocal()
    try:
        setting = db.query(SettingDB).filter(SettingDB.key == "household_shopping_list").first()
        if setting:
            setting.value = json.dumps(items, ensure_ascii=False)
        else:
            setting = SettingDB(key="household_shopping_list", value=json.dumps(items, ensure_ascii=False))
            db.add(setting)
        db.commit()
        return True
    except Exception as e:
        logger.error(f"Failed to save shopping list: {e}")
        db.rollback()
        return False
    finally:
        db.close()


# ==========================================
# COMMAND HANDLERS
# ==========================================

def get_partner_menu() -> InlineKeyboardMarkup:
    """Returns the main interactive menu for Hanni."""
    buttons = [
        [
            InlineKeyboardButton(text="📅 Jimmys schema", callback_data="p_jimmy_schedule"),
            InlineKeyboardButton(text="📋 Mitt schema", callback_data="p_my_schedule"),
        ],
        [
            InlineKeyboardButton(text="🛒 Inköpslistan", callback_data="p_shopping_list"),
            InlineKeyboardButton(text="💡 Hjälp & Tips", callback_data="p_help"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@partner_dp.message(Command("start", "menu"))
async def cmd_start(message: types.Message):
    """Welcomes Hanni with a friendly greeting and interactive menu."""
    if not await verify_partner(message):
        return
    name = message.from_user.first_name or "Hanni"
    await message.answer(
        f"Hej {name}! 👋😊\n\n"
        f"Jag är din personliga assistent. Jag kan hjälpa dig med:\n"
        f"• 📅 Se Jimmys jobbschema\n"
        f"• ✏️ Lägga in ditt eget schema\n"
        f"• 🔔 Skicka påminnelser till Jimmy\n"
        f"• 🛒 Gemensam inköpslista\n\n"
        f"Du kan skriva till mig på **svenska** eller **somaliska** 🇸🇪🇸🇴\n\n"
        f"💡 _Prova att skriva: 'Hur jobbar Jimmy idag?'_",
        reply_markup=get_partner_menu(),
        parse_mode="Markdown"
    )


@partner_dp.message(Command("schema"))
async def cmd_schema(message: types.Message):
    """Parses a pasted work schedule and bulk-inserts into Hanni's calendar."""
    if not await verify_partner(message):
        return

    raw_text = message.text.replace("/schema", "", 1).strip()
    if not raw_text:
        await message.reply(
            "ℹ️ Skriv ditt jobbschema efter /schema.\n"
            "Exempel:\n"
            "/schema\n"
            "5/3 Ons: 07:00-16:00\n"
            "7/3 Fre: 08:00-15:30\n\n"
            "💡 Du kan också bara skriva naturligt: _'Jag jobbar 8 till 17 imorgon'_",
            parse_mode="Markdown"
        )
        return

    events = parse_work_schedule(raw_text)
    if not events:
        await message.reply(
            "❌ Jag kunde inte förstå schemat. Prova så här:\n"
            "`5/3 Ons: 07:00-16:00`\n"
            "eller\n"
            "_Jag jobbar 8 till 17 imorgon_",
            parse_mode="Markdown"
        )
        return

    # Insert events into calendar with owner="partner"
    from database import SessionLocal
    from models import EventDB, SystemLogDB

    db = SessionLocal()
    added = 0
    details = []
    try:
        for evt in events:
            new_event = EventDB(
                id=str(uuid.uuid4()),
                start_date=evt["start_date"],
                start_time=evt["start_time"],
                end_time=evt.get("end_time"),
                description=evt["description"],
                category="Work",
                priority="Medium",
                agent_id="PartnerSchemaImport",
                owner="partner",
                reminder_sent=True
            )
            db.add(new_event)
            added += 1
            details.append(f"{evt['start_date']} {evt['start_time']}-{evt.get('end_time', '?')}")

        audit = SystemLogDB(
            action_type="partner_schema_import",
            details=f"Hanni imported {added} work shifts via Partner Bot."
        )
        db.add(audit)
        db.commit()

        await message.reply(
            f"✅ **Schema sparat!** 🎉\n\n"
            f"**{added} arbetspass** har lagts till i din kalender:\n\n"
            + "\n".join([f"• {d}" for d in details]),
            parse_mode="Markdown"
        )
    except Exception as e:
        db.rollback()
        await message.reply(f"❌ Något gick fel: {str(e)}")
    finally:
        db.close()


# ==========================================
# CALLBACK HANDLERS (Inline Keyboard)
# ==========================================

@partner_dp.callback_query()
async def partner_callbacks(callback: types.CallbackQuery):
    """Handles inline keyboard button presses."""
    if PARTNER_USER_ID and str(callback.from_user.id) != PARTNER_USER_ID:
        await callback.answer("⛔ Åtkomst nekad", show_alert=True)
        return

    await callback.answer()

    if callback.data == "p_jimmy_schedule":
        schedule = get_jimmy_schedule(days_ahead=1)
        await callback.message.answer(schedule, parse_mode="Markdown")

    elif callback.data == "p_my_schedule":
        schedule = get_hanni_schedule(days_ahead=1)
        await callback.message.answer(schedule, parse_mode="Markdown")

    elif callback.data == "p_shopping_list":
        items = get_shopping_list()
        if items:
            list_text = "🛒 **Inköpslistan:**\n\n"
            for i, item in enumerate(items, 1):
                list_text += f"{i}. {item}\n"
            list_text += "\n_Skriv 'rensa listan' för att tömma den._"
        else:
            list_text = "🛒 Inköpslistan är tom! 🎉\n\n_Skriv t.ex. 'vi behöver mjölk och bröd' för att lägga till._"
        await callback.message.answer(list_text, parse_mode="Markdown")

    elif callback.data == "p_help":
        await callback.message.answer(
            "💡 **Saker du kan skriva till mig:**\n\n"
            "📅 **Schema:**\n"
            "• _'Hur jobbar Jimmy idag?'_\n"
            "• _'Jag jobbar 7 till 15 på fredag'_\n"
            "• _'/schema 5/3: 07-16'_\n\n"
            "🔔 **Påminnelser:**\n"
            "• _'Påminn Jimmy att hämta barnen kl 16'_\n"
            "• _'Säg till Jimmy att köpa mjölk'_\n\n"
            "🛒 **Inköpslistan:**\n"
            "• _'Vi behöver mjölk och bröd'_\n"
            "• _'Vad ska handlas?'_\n"
            "• _'Rensa listan'_\n\n"
            "🇸🇴 _Waxaad igala hadli kartaa Af-Soomaali!_",
            parse_mode="Markdown"
        )


# ==========================================
# CHAT HANDLER (AI-Powered Conversation)
# ==========================================

partner_sessions = {}


@partner_dp.message()
async def partner_chat_handler(message: types.Message):
    """Handles free-text conversation with Hanni using AI."""
    if not await verify_partner(message):
        return

    user_text = message.text
    if not user_text:
        return

    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Hanni"

    await partner_bot.send_chat_action(chat_id=user_id, action="typing")

    # --- DETERMINISTIC SHORTCUTS (no LLM needed) ---

    text_lower = user_text.lower()

    # 1. Check if she's asking about Jimmy's schedule
    jimmy_keywords = ["jimmy", "min man", "han jobbar", "hur jobbar", "når jobbar",
                       "ninkeygii", "ninkeyga"]
    if any(kw in text_lower for kw in jimmy_keywords):
        schedule = get_jimmy_schedule(days_ahead=7)
        tips = "\n\n💡 _Tips: Skriv 'Påminn Jimmy att...' för att skicka honom en påminnelse._"
        await message.answer(schedule + tips, parse_mode="Markdown")
        return

    # 2. Check if she wants to add her own schedule
    work_keywords = ["jobbar", "arbetar", "jobb", "shaqeyno", "shaqo"]
    time_pattern = re.search(r'\d{1,2}\s*(?:till|to|-|–|:)\s*\d{1,2}', text_lower)
    if any(kw in text_lower for kw in work_keywords) and time_pattern:
        events = parse_work_schedule(user_text)
        if events:
            from database import SessionLocal
            from models import EventDB, SystemLogDB

            db = SessionLocal()
            added_details = []
            try:
                for evt in events:
                    new_event = EventDB(
                        id=str(uuid.uuid4()),
                        start_date=evt["start_date"],
                        start_time=evt["start_time"],
                        end_time=evt.get("end_time"),
                        description=evt["description"],
                        category="Work",
                        priority="Medium",
                        agent_id="PartnerNaturalInput",
                        owner="partner",
                        reminder_sent=True
                    )
                    db.add(new_event)
                    added_details.append(f"{evt['start_date']} kl {evt['start_time']}-{evt.get('end_time', '?')}")

                db.commit()
                await message.answer(
                    f"✅ Klart! Jag har lagt in ditt jobb: 📅\n\n"
                    + "\n".join([f"• {d}" for d in added_details])
                    + "\n\n💡 _Tips: Skriv 'mitt schema' för att se din kalender._",
                    parse_mode="Markdown"
                )
            except Exception as e:
                db.rollback()
                await message.answer(f"❌ Kunde inte spara: {e}")
            finally:
                db.close()
            return

    # 3. Check if she wants to remind Jimmy
    remind_keywords = ["påminn jimmy", "säg till jimmy", "påminn min man",
                       "tell jimmy", "remind jimmy",
                       "u sheeg jimmy", "xusuusi jimmy"]
    if any(kw in text_lower for kw in remind_keywords):
        # Extract the reminder text (everything after the keyword match)
        reminder_text = user_text
        for kw in remind_keywords:
            if kw in text_lower:
                idx = text_lower.index(kw) + len(kw)
                reminder_text = user_text[idx:].strip()
                # Remove leading "att" or "to" or "in"
                reminder_text = re.sub(r'^(att|to|in)\s+', '', reminder_text, flags=re.IGNORECASE).strip()
                break

        # Try to extract a time
        time_match = re.search(r'(?:kl\.?\s*)?(\d{1,2}[:\.]?\d{0,2})', reminder_text)
        reminder_time = _normalize_time(time_match.group(1)) if time_match else "17:00"

        # Clean up the description (remove the time part)
        clean_desc = re.sub(r'(?:kl\.?\s*)?\d{1,2}[:\.]?\d{0,2}', '', reminder_text).strip()
        if not clean_desc:
            clean_desc = reminder_text

        now = datetime.now(SWEDISH_TZ)
        today_str = now.strftime("%Y-%m-%d")

        from calendar_agent import calendar_agent
        success = calendar_agent.add_event(
            start_date=today_str,
            start_time=reminder_time,
            description=f"📩 Från Hanni: {clean_desc}",
            agent_id="PartnerReminder",
            owner="ceo",
            is_reminder=True
        )

        if success:
            await message.answer(
                f"✅ Klart! Jag påminner Jimmy kl {reminder_time} 🔔\n"
                f"_\"{clean_desc}\"_\n\n"
                f"💡 _Han får en notis i sin Telegram._",
                parse_mode="Markdown"
            )
        else:
            await message.answer("❌ Kunde inte skapa påminnelsen. Försök igen!")
        return

    # 4. Shopping list - add items
    shopping_add_keywords = ["behöver", "köpa", "handla", "vi behöver", "köp",
                              "slut på", "är slut", "iibso", "waa naga dhammaaday"]
    if any(kw in text_lower for kw in shopping_add_keywords):
        # Extract items (crude but effective NLP)
        items_text = user_text
        for kw in shopping_add_keywords:
            items_text = re.sub(re.escape(kw), '', items_text, flags=re.IGNORECASE)
        # Split by commas, "och", "and", "iyo"
        raw_items = re.split(r'[,]|\boch\b|\band\b|\biyo\b', items_text)
        new_items = [item.strip().strip('.!?') for item in raw_items if item.strip() and len(item.strip()) > 1]

        if new_items:
            current_list = get_shopping_list()
            current_list.extend(new_items)
            save_shopping_list(current_list)
            await message.answer(
                f"🛒 Lagt till på inköpslistan:\n"
                + "\n".join([f"• {item}" for item in new_items])
                + f"\n\n📋 Totalt {len(current_list)} saker på listan.",
                parse_mode="Markdown"
            )
            return

    # 5. Shopping list - view
    if any(kw in text_lower for kw in ["vad ska handlas", "inköpslistan", "shopping",
                                         "maxaa la iibsanayaa", "liiska"]):
        items = get_shopping_list()
        if items:
            list_text = "🛒 **Inköpslistan:**\n\n"
            for i, item in enumerate(items, 1):
                list_text += f"{i}. {item}\n"
        else:
            list_text = "🛒 Inköpslistan är tom! Bra jobbat! 🎉"
        await message.answer(list_text, parse_mode="Markdown")
        return

    # 6. Shopping list - clear
    if any(kw in text_lower for kw in ["rensa listan", "töm listan", "clear list"]):
        save_shopping_list([])
        await message.answer("✅ Inköpslistan är nu tömd! 🧹✨")
        return

    # 7. "My schedule"
    if any(kw in text_lower for kw in ["mitt schema", "min kalender", "mina jobb",
                                         "jadwalkeyga", "shaqadeyda"]):
        schedule = get_hanni_schedule(days_ahead=7)
        await message.answer(schedule, parse_mode="Markdown")
        return

    # --- FALLBACK: Use AI for anything else ---
    try:
        from router import router

        if user_id not in partner_sessions:
            partner_sessions[user_id] = []
        history = partner_sessions[user_id]

        # Enrich with calendar context
        jimmy_cal = get_jimmy_schedule(days_ahead=3)
        hanni_cal = get_hanni_schedule(days_ahead=3)
        context = f"\n[KONTEXT: {jimmy_cal}\n{hanni_cal}]"

        def ask_ai():
            return router.ask_cortex(
                user_prompt=user_text + context,
                history=history,
                user_name=user_name,
                system_prompt=PARTNER_SYSTEM_PROMPT
            )

        reply = await asyncio.to_thread(ask_ai)

        history.append({"role": "user", "content": user_text})
        history.append({"role": "assistant", "content": reply})
        partner_sessions[user_id] = history[-20:]

        await message.answer(reply, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Partner chat error: {e}")
        await message.answer(
            "❌ Något gick fel. Försök igen om en stund! 💛\n\n"
            "💡 _Tips: Skriv /menu för att se vad jag kan hjälpa dig med._"
        )


# ==========================================
# MORNING BRIEFING FOR HANNI
# ==========================================

async def send_partner_morning_briefing():
    """Sends a friendly morning briefing to Hanni with schedule overview."""
    if not PARTNER_USER_ID:
        logger.warning("No PARTNER_USER_ID set, skipping morning briefing for partner.")
        return

    jimmy_schedule = get_jimmy_schedule(days_ahead=1)
    hanni_schedule = get_hanni_schedule(days_ahead=1)
    shopping = get_shopping_list()

    now = datetime.now(SWEDISH_TZ)
    weekday_names = ["Måndag", "Tisdag", "Onsdag", "Torsdag", "Fredag", "Lördag", "Söndag"]
    day_name = weekday_names[now.weekday()]

    briefing = (
        f"☀️ **God morgon Hanni!** 💛\n"
        f"Idag är det {day_name} {now.strftime('%d/%m')}.\n\n"
        f"{jimmy_schedule}\n\n"
        f"{hanni_schedule}\n"
    )

    if shopping:
        briefing += f"\n🛒 **Inköpslistan** ({len(shopping)} saker):\n"
        for item in shopping[:5]:
            briefing += f"• {item}\n"
        if len(shopping) > 5:
            briefing += f"_...och {len(shopping) - 5} till._\n"

    briefing += (
        "\n😊 Ha en underbar dag!\n\n"
        "💡 _Tips: Skriv 'Påminn Jimmy att hämta barnen kl 16' "
        "om du behöver skicka honom ett meddelande._"
    )

    try:
        await partner_bot.send_message(
            chat_id=PARTNER_USER_ID,
            text=briefing,
            parse_mode="Markdown"
        )
        logger.info("Sent morning briefing to Hanni.")
    except Exception as e:
        logger.error(f"Failed to send morning briefing to Hanni: {e}")


# ==========================================
# CROSS-BOT MESSAGING (CEO -> Partner)
# ==========================================

async def send_message_to_hanni(text: str):
    """Sends a message from the CEO bot to Hanni's bot."""
    if not PARTNER_USER_ID:
        logger.warning("No PARTNER_USER_ID set, cannot send message to Hanni.")
        return False
    try:
        await partner_bot.send_message(
            chat_id=PARTNER_USER_ID,
            text=text,
            parse_mode="Markdown"
        )
        return True
    except Exception as e:
        logger.error(f"Failed to send message to Hanni: {e}")
        return False


# ==========================================
# ONE-TIME WELCOME MESSAGE
# ==========================================

async def send_welcome_to_hanni():
    """Sends a one-time welcome and intro message to Hanni when the bot first launches."""
    if not PARTNER_USER_ID:
        logger.warning("No PARTNER_USER_ID set, skipping welcome message.")
        return
    try:
        await partner_bot.send_message(
            chat_id=PARTNER_USER_ID,
            text=(
                "Hej Hanni! 👋❤️\n\n"
                "Jag är din nya personliga assistent från Jimmy! 🤖✨\n\n"
                "Här är vad jag kan hjälpa dig med:\n\n"
                "📅 **Schema:**\n"
                "• Skriv _'Hur jobbar Jimmy idag?'_ för att se hans schema\n"
                "• Skriv _'Jag jobbar 8 till 17 imorgon'_ för att lägga in ditt jobb\n\n"
                "🔔 **Påminnelser:**\n"
                "• Skriv _'Påminn Jimmy att hämta barnen kl 16'_\n"
                "• Han får en notis direkt i sin telefon! 📱\n\n"
                "🛒 **Inköpslista:**\n"
                "• Skriv _'Vi behöver mjölk och bröd'_ för att lägga till\n"
                "• Skriv _'Vad ska handlas?'_ för att se listan\n\n"
                "🇸🇴 Du kan också skriva till mig på **somaliska**!\n\n"
                "Tryck på /menu när som helst för att se knapparna. 😊"
            ),
            parse_mode="Markdown"
        )
        logger.info("Sent welcome message to Hanni.")
    except Exception as e:
        logger.error(f"Failed to send welcome to Hanni: {e}")


# ==========================================
# POLLING ENTRY POINT
# ==========================================

async def start_partner_polling():
    """Starts the Telegram polling loop for the Partner Bot."""
    logger.info("Starting Telegram polling for Sintari Partner Bot (Hanni)...")
    await partner_dp.start_polling(partner_bot)
