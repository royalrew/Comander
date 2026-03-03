import yaml
import logging
from audit_module import audit_module
from router import router
from reporter import reporter_instance
import os

logger = logging.getLogger(__name__)

async def perform_midweek_review():
    """
    The Consigliere's accountability loop.
    Compares the CEO's active codebase work against the long-term goals in ceo_profile.yaml.
    """
    logger.info("Initiating Mid-Week CEO Review...")
    
    # 1. Read the Strategy
    profile_path = os.path.join(os.path.dirname(__file__), "ceo_profile.yaml")
    ceo_goals = ""
    try:
        with open(profile_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            goals = data.get("identity", {}).get("ultimate_goal", "Inga specifika mål angivna.")
            focus = data.get("identity", {}).get("current_business_focus", "Inget specifikt fokus.")
            biz = data.get("business_details", {}).get("description", "")
            ceo_goals = f"Mål: {goals}\nFokus: {focus}\nBusiness: {biz}"
    except Exception as e:
        logger.error(f"Failed to read ceo_profile.yaml: {e}")
        ceo_goals = "Kunde inte läsa uppsatta mål."

    # 2. Check the Reality (What has the CEO coded the last 3 days?)
    # Using 72 hours to cover Mon-Wed activity
    recent_activity = audit_module.get_recent_activity(hours=72)
    
    reality_context = ""
    if "Inga kod-commits" in recent_activity or "Inget" in recent_activity or "Kunde inte komma åt" in recent_activity:
        reality_context = f"GitHub Loggar:\n{recent_activity}\n(Antingen har CEO inte pushat något, eller så är repot dolt utan token)."
    else:
        reality_context = f"VD:n har under de senaste 3 dagarna pushat följande commits till GitHub:\n{recent_activity}"

    # 3. The Analysis
    system_prompt = (
        "Du är The Commander, en strategisk accountability partner (Consigliere). "
        "Ditt jobb är att jämföra VD:ns långsiktiga MÅL med VAD SOM FAKTISKT HAR GJORTS i koden denna vecka. "
        "Agera som en tuff men stöttande COO. "
        "Om framsteget är långsamt eller noll: ställ en direkt, ifrågasättande fråga varför. "
        "Om framsteget är i linje med målen: fira det kortfattat. "
        "Håll det under 3-4 meningar. Avsluta alltid med en rak fråga om nästa steg. "
        "Formatera svaret snyggt för Telegram (använd emojis)."
    )
    
    user_prompt = f"CEO MÅL:\n{ceo_goals}\n\nVECKANS TILLSTÅND (REALITY):\n{reality_context}"

    try:
        import asyncio
        review_text = await asyncio.to_thread(
            router.ask_cortex_direct,
            user_prompt=user_prompt,
            system_prompt=system_prompt
        )
        final_message = f"⚖️ **MID-WEEK REVIEW**\n\n{review_text}"
        await reporter_instance.send_alert(final_message)
    except Exception as e:
        logger.error(f"Failed to generate midweek review: {e}")
        await reporter_instance.send_alert("Kunde inte generera Mid-Week Review på grund av ett serverfel.")
