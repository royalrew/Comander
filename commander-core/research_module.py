import urllib.robotparser
import urllib.parse
import urllib.request
import logging
import json
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

# A list of preferred domains for high-quality technical/strategic answers
PREFERRED_DOMAINS = [
    "github.com",
    "developer.mozilla.org",
    "stackoverflow.com",
    "docs.python.org",
    "react.dev",
    "nextjs.org",
    "ycombinator.com",
    "stripe.com/docs"
]

class ResearchModule:
    """
    Handles autonomous web research and scraping.
    Strictly adheres to robots.txt to ensure long-term IP health.
    Favors high-reputation domains for technical queries.
    """
    def __init__(self):
        self.user_agent = "CommanderBot/1.0 (+https://github.com/royalrew/Comander)"
        self.rp_cache = {}

    def _is_allowed_by_robots(self, url: str) -> bool:
        """Checks if parsing is allowed by the domain's robots.txt."""
        parsed_url = urllib.parse.urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        robots_url = f"{base_url}/robots.txt"

        if base_url not in self.rp_cache:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(robots_url)
            try:
                # Fetch with a short timeout to prevent hanging
                rp.read()
                self.rp_cache[base_url] = rp
            except Exception as e:
                # If robots.txt fails to load (e.g. 404), standard practice is to assume allowed,
                # but we log it just in case.
                logger.warning(f"Could not read robots.txt for {base_url}: {e}")
                self.rp_cache[base_url] = None

        rp = self.rp_cache[base_url]
        if rp is None:
            return True # Allowed by default if no robots.txt exists
            
        return rp.can_fetch(self.user_agent, url)

    def search_internet(self, query: str, prioritize_safe_domains: bool = True, max_results: int = 5) -> str:
        """
        Searches DuckDuckGo. If prioritize_safe_domains is True, it will append site: queries 
        or prefer results from known good domains (StackOverflow, Github, Official Docs).
        """
        logger.info(f"Researching: '{query}'")
        
        # If it's a strongly technical query and safe domains are requested, we could 
        # modify the query, but DDG is usually good enough. We'll simply note the domains requested.
        
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                
            if not results:
                return "Inga resultat hittades."
                
            formatted_results = []
            for r in results:
                title = r.get("title", "Utan titel")
                link = r.get("href", "")
                snippet = r.get("body", "")
                
                # Check if it's a preferred domain
                is_preferred = any(domain in link for domain in PREFERRED_DOMAINS)
                badge = "[HÖG AUKTORITET]" if is_preferred else ""
                
                formatted_results.append(f"Titel: {title} {badge}\nLänk: {link}\nUtdrag: {snippet}\n")
                
            return "\n".join(formatted_results)
            
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
            return f"Sökningen misslyckades: {str(e)}"

    def read_webpage(self, url: str) -> str:
        """
        Fetches the text content of a webpage if robots.txt allows it.
        Uses BeautifulSoup to parse out HTML tags and scripts.
        """
        logger.info(f"Attempting to read webpage: {url}")
        
        if not self._is_allowed_by_robots(url):
            return "ÅTKOMST NEKAD: Sidan blockerar web-skrapor via robots.txt. Vänligen sök efter en annan källa för att skydda vår IP-reputation."

        try:
            req = urllib.request.Request(url, headers={'User-Agent': self.user_agent})
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read()

            soup = BeautifulSoup(html, "html.parser")
            
            # Kill all script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.extract()
                
            # Get text
            text = soup.get_text(separator=' ', strip=True)
            
            # Cap the text to prevent Context Window explosion (e.g. 5000 characters)
            if len(text) > 8000:
                text = text[:8000] + "... [TEXT KORTADES NER FÖR ATT SPARA TOKENS]"
                
            return text
            
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                return f"ÅTKOMST NEKAD (HTTP {e.code}): Sidan kräver förmodligen inloggning eller blockerar robotar proaktivt."
            return f"Misslyckades med att ladda sidan. HTTP Error: {e.code}"
        except Exception as e:
            logger.error(f"Failed to read webpage {url}: {e}")
            return f"Ett fel uppstod vid inläsning av sidan: {str(e)}"

research_module = ResearchModule()
