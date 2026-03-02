import os
import time
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class OvernightAudit:
    """
    Acts as the Strategic Tech Lead scanning the CEO's active project overnight.
    Reads files modified in the last 24 hours and generates an architectural review.
    """
    
    def __init__(self):
        # Default to ALLOWED_MISSIONS_DIR if ACTIVE_PROJECT_DIR is not set
        self.project_dir = os.getenv("ACTIVE_PROJECT_DIR", os.getenv("ALLOWED_MISSIONS_DIR", ""))
        self.ignore_dirs = {".git", "node_modules", "venv", "__pycache__", ".next", "dist", "build"}

    def get_recent_files(self, hours: int = 24, max_files: int = 5) -> list[str]:
        """Finds the most recently modified code files."""
        if not self.project_dir or not os.path.exists(self.project_dir):
            logger.warning("ACTIVE_PROJECT_DIR is not set or invalid.")
            return []

        recent_files = []
        current_time = time.time()
        cutoff_time = current_time - (hours * 3600)

        for root, dirs, files in os.walk(self.project_dir):
            # Mutate the dirs list in-place to ignore certain directories
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            
            for file in files:
                if not file.endswith(('.py', '.tsx', '.ts', '.js', '.jsx', '.css', '.md')):
                    continue
                    
                filepath = os.path.join(root, file)
                try:
                    mtime = os.path.getmtime(filepath)
                    if mtime >= cutoff_time:
                        recent_files.append((filepath, mtime))
                except OSError:
                    continue
                    
        # Sort by most recently modified, take top `max_files`
        recent_files.sort(key=lambda x: x[1], reverse=True)
        return [f[0] for f in recent_files[:max_files]]

    def generate_audit_report(self) -> str:
        """
        Gathers recent code context and asks Cortex to perform an architectural review.
        """
        recent_files = self.get_recent_files()
        
        if not recent_files:
            return "Ingen ny kod skriven senaste dygnet. Fokusera på mål i ceo_profile.yaml."

        context_string = ""
        for filepath in recent_files:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Cap content to prevent massive context window bloat
                    if len(content) > 3000:
                        content = content[:3000] + "... [TRUNCATED]"
                    
                    filename = os.path.basename(filepath)
                    context_string += f"--- {filename} ---\n{content}\n\n"
            except Exception as e:
                logger.error(f"Failed to read {filepath} for audit: {e}")

        # Import dynamically to avoid circular dependencies
        from router import router
        
        system_prompt = (
            "Du är en Senior Tech Lead och CTO Consultant (Consultant Mode). "
            "Du granskar koden som CEO:en skrev igår natt. "
            "Ge en VÄLDIGT kort, slagkraftig review (max 3-4 meningar). "
            "Fokusera på arkitektur, säkerhet eller skalbarhet. Kritisera konstruktivt om du ser anti-patterns "
            "men beröm om det är snyggt. Formatera som en direkt, professionell telegram-bulletpoint."
        )
        
        user_prompt = f"CEO:ns senaste kod från projektmappen:\n\n{context_string}"
        
        try:
            logger.info("Executing the Overnight Audit via Cortex...")
            review = router.ask_cortex(user_prompt, system_prompt=system_prompt)
            return f"🔍 **Overnight Tech Audit:**\n{review}"
        except Exception as e:
            logger.error(f"Audit generation failed: {e}")
            return "Overnight Audit failed. Cortex unreachable."

audit_module = OvernightAudit()
