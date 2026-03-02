import os
import requests
import logging
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class OvernightAudit:
    """
    Acts as the Strategic Tech Lead tracking the CEO's progression.
    Reads recent commits from the specified GitHub repository to generate an architectural review.
    """
    
    def __init__(self):
        self.github_repo = os.getenv("GITHUB_REPO", "royalrew/Comander")
        self.github_token = os.getenv("GITHUB_TOKEN", "") # Optional, needed if repo is private

    def get_recent_activity(self, hours: int = 72) -> str:
        """Fetches commit messages and changed files from the GitHub API."""
        if not self.github_repo:
            return "Inget GITHUB_REPO definierat i .env."

        cutoff_date = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
        url = f"https://api.github.com/repos/{self.github_repo}/commits?since={cutoff_date}"
        
        headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            commits = response.json()
            
            if not commits:
                return "Inga kod-commits pushade till GitHub under den valda tidsperioden."
                
            activity_log = []
            for commit in commits[:10]: # Analyze max 10 latest commits
                msg = commit.get("commit", {}).get("message", "Ingen commit-meddelande")
                author = commit.get("commit", {}).get("author", {}).get("name", "Okänd")
                date = commit.get("commit", {}).get("author", {}).get("date", "")
                activity_log.append(f"[{date}] {author}: {msg}")
                
            return "\n".join(activity_log)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub API Error: {e}")
            if hasattr(e, 'response') and e.response is not None and e.response.status_code == 404:
                return f"Kunde inte komma åt repot '{self.github_repo}'. Kontrollera att det är publikt, eller lägg till GITHUB_TOKEN i .env för privata repor."
            return f"Misslyckades med att hämta GitHub-historik: {e}"

    def generate_audit_report(self) -> str:
        """
        Gathers recent GitHub activity and asks Cortex to perform an architectural review.
        """
        recent_activity = self.get_recent_activity()
        
        # Import dynamically to avoid circular dependencies
        from router import router
        
        system_prompt = (
            "Du är en Senior Tech Lead och CTO Consultant (Consultant Mode). "
            "Du granskar VD:ns senaste kod-commits från GitHub. "
            "Ge en VÄLDIGT kort, slagkraftig review (max 3-4 meningar). "
            "Fokusera på framdrift, arkitektur eller säkerhet baserat på commit-meddelandena. Kritisera konstruktivt om du ser anti-patterns (ex. stökiga commits) "
            "men beröm om det är snyggt och strategiskt. Formatera som en direkt, professionell telegram-bulletpoint."
        )
        
        user_prompt = f"CEO:ns senaste GitHub-aktivitet ({self.github_repo}):\n\n{recent_activity}"
        
        try:
            logger.info("Executing the Overnight Audit via Cortex...")
            review = router.ask_cortex(user_prompt, system_prompt=system_prompt)
            return f"🔍 **Overnight Tech Audit (via GitHub):**\n{review}"
        except Exception as e:
            logger.error(f"Audit generation failed: {e}")
            return "Overnight Audit failed. Cortex unreachable."

audit_module = OvernightAudit()
