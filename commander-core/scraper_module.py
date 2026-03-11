import os
import json
import logging
import asyncio
from typing import Optional, Dict, Any
from urllib.parse import urlparse
import urllib.robotparser
from pydantic import BaseModel

try:
    from crawl4ai import AsyncWebCrawler
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False

logger = logging.getLogger("Clawbot")

class ScrapeResult(BaseModel):
    url: str
    markdown: str
    success: bool
    error: Optional[str] = None
    html: Optional[str] = None # Saved for R2 archiving

class ScraperModule:
    """
    Clawbot Engine: The Executor.
    Uses Crawl4AI and Playwright for headless browser scraping.
    Prioritizes ethical scraping via robots.txt and proxy rotation.
    """
    def __init__(self):
        self.user_agent = "CommanderBot/2.0 (+https://github.com/royalrew/Comander)"
        self.rp_cache: Dict[str, Optional[urllib.robotparser.RobotFileParser]] = {}
        self.proxy = os.getenv("BRIGHT_DATA_PROXY") # Optional proxy

    async def _check_robots_txt(self, url: str) -> bool:
        """Ethical check: Validate robots.txt before scraping."""
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        robots_url = f"{base_url}/robots.txt"

        if base_url not in self.rp_cache:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(robots_url)
            try:
                # Read robots.txt without blocking the event loop
                await asyncio.to_thread(rp.read)
                self.rp_cache[base_url] = rp
            except Exception as e:
                logger.warning(f"Could not read robots.txt for {base_url}: {e}")
                self.rp_cache[base_url] = None

        rp = self.rp_cache[base_url]
        if rp is None:
            return True # Allow by default if no robots.txt exists or it's unreachable
            
        return rp.can_fetch(self.user_agent, url)

    async def scrape_url(self, url: str, bypass_ethics: bool = False) -> ScrapeResult:
        """
        Headless scraping using Crawl4AI.
        If bypass_ethics is True, "The Commander" explicitly authorized the scrape despite robots.txt.
        """
        logger.info(f"Clawbot executing scrape on: {url}")
        
        if not CRAWL4AI_AVAILABLE:
            return ScrapeResult(
                url=url,
                markdown="",
                success=False,
                error="Crawl4AI is not installed. Please run: pip install crawl4ai playwright && playwright install"
            )

        if not bypass_ethics:
            is_allowed = await self._check_robots_txt(url)
            if not is_allowed:
                return ScrapeResult(
                    url=url,
                    markdown="",
                    success=False,
                    error="ACCESS DENIED: robots.txt prohibits scraping. Ethics override required from The Commander.",
                )

        try:
            kwargs = {}
            if self.proxy:
                kwargs['proxy'] = self.proxy
                
            async with AsyncWebCrawler(**kwargs) as crawler:
                # word_count_threshold helps remove noise (nav/footers)
                result = await crawler.arun(
                    url=url, 
                    word_count_threshold=10, 
                    bypass_cache=True,
                )

                if result.success:
                    logger.info(f"Clawbot successfully extracted {len(result.markdown)} chars of markdown.")
                    return ScrapeResult(
                        url=url,
                        markdown=result.markdown,
                        success=True,
                        html=result.html
                    )
                else:
                    return ScrapeResult(
                        url=url,
                        markdown="",
                        success=False,
                        error=f"Crawl4AI engine failed: {result.error_message}"
                    )
                    
        except Exception as e:
            logger.error(f"Clawbot encountered a fatal error during extraction: {e}")
            return ScrapeResult(
                url=url,
                markdown="",
                success=False,
                error=str(e)
            )

scraper_module = ScraperModule()
