import os
import asyncio
import json
import logging
import uuid
import boto3
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from aiobotocore.session import get_session
from playwright.async_api import async_playwright
from memory_module import memory_bank
from typing import List, Dict, Any, Set

logger = logging.getLogger("HunterSwarm")
logger.setLevel(logging.INFO)

class HunterSwarm:
    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(self.max_concurrent)
        
        # Safe Zone check
        self.safe_zone = os.getenv("ACTIVE_PROJECT_DIR") or os.getenv("ALLOWED_MISSIONS_DIR")
        if not self.safe_zone:
            logger.warning("No Safe Zone (ACTIVE_PROJECT_DIR) found in .env. Falling back to local ./tmp")
            self.safe_zone = os.path.join(os.path.dirname(__file__), "tmp")
        os.makedirs(self.safe_zone, exist_ok=True)
        
        # R2 Config
        self.r2_access_key = os.getenv("CLOUDFLARE_R2_ACCESS_KEY")
        self.r2_secret_key = os.getenv("CLOUDFLARE_R2_SECRET_KEY")
        self.account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
        self.bucket_name = os.getenv("CLOUDFLARE_R2_BUCKET_NAME", "sintari-data-lake")
        
        self.visited_urls: Set[str] = set()

    async def _async_upload_to_r2(self, content: bytes, filename: str, r2_prefix: str = "hunter_dump", content_type: str = "application/json"):
        """Asynchronously streams data to Cloudflare R2 using aiobotocore. Falls back to Safe Zone on disk."""
        clean_prefix = r2_prefix.strip("/")
        
        # Local Fallback path
        local_dir = os.path.join(self.safe_zone, clean_prefix.replace("/", os.sep))
        os.makedirs(local_dir, exist_ok=True)
        local_path = os.path.join(local_dir, filename)

        if not self.r2_access_key or not self.account_id:
            logger.warning(f"R2 credentials missing. Saving {filename} locally to Safe Zone.")
            with open(local_path, "wb") as f:
                f.write(content)
            return True

        endpoint_url = f"https://{self.account_id}.r2.cloudflarestorage.com"
        session = get_session()
        
        try:
            async with session.create_client(
                's3',
                region_name='auto',
                endpoint_url=endpoint_url,
                aws_access_key_id=self.r2_access_key,
                aws_secret_access_key=self.r2_secret_key
            ) as client:
                await client.put_object(
                    Bucket=self.bucket_name,
                    Key=f"{clean_prefix}/{filename}",
                    Body=content,
                    ContentType=content_type
                )
            logger.info(f"Successfully streamed {filename} to R2.")
            return True
        except Exception as e:
            logger.error(f"Async R2 upload failed for {filename}: {e}. Falling back to Safe Zone.")
            with open(local_path, "wb") as f:
                f.write(content)
            return True

    def _index_high_value_intel(self, source_url: str, content: str):
        """Extracts high-value snippets and saves them to the Postgres MemoryBank."""
        # Simple heuristic for MVP: search for common keywords.
        # In a real scenario, this would trigger a fast LLM pass or advanced Regex.
        keywords = ["pricing", "api", "token", "password", "secret", "cost", "$"]
        intel_fragments = []
        
        # Simple extraction logic
        lower_content = content.lower()
        if any(kw in lower_content for kw in keywords):
            preview = content[:200].replace('\n', ' ')
            intel = f"High-Value Intel found at {source_url}: {preview}..."
            memory_bank.store_memory(category="HunterIntel", text=intel)
            logger.info(f"Indexed high-value insight from {source_url} to Postgres.")

    async def _process_target(self, url: str, context, queue: asyncio.Queue, r2_prefix: str, extract_targets: List[str]):
        """Navigates to a single URL, intercepts XHR, and extracts logic."""
        async with self.semaphore:
            if url in self.visited_urls:
                return
            self.visited_urls.add(url)
            
            logger.info(f"Hunter swarming target: {url}")
            page = await context.new_page()
            
            intercepted_data = {}

            # X-Ray Vision: Intercept network routes asynchronously
            async def handle_response(response):
                try:
                    # Target JSON API responses
                    if "application/json" in response.headers.get("content-type", ""):
                        req_url = response.url
                        try:
                            json_data = await response.json()
                            intercepted_data[req_url] = json_data
                            
                            # Stream raw JSON to R2 immediately
                            json_bytes = json.dumps(json_data).encode('utf-8')
                            filename = f"xhrcall_{uuid.uuid4().hex[:6]}.json"
                            await self._async_upload_to_r2(json_bytes, filename, r2_prefix=r2_prefix, content_type="application/json")
                            self._index_high_value_intel(req_url, str(json_data))
                            
                        except Exception as parse_e:
                            pass # Probably not valid JSON despite header
                except Exception as e:
                    pass

            page.on("response", handle_response)
            
            try:
                # Wait until network is relatively idle, timeout after 15s to keep moving
                await page.goto(url, wait_until="networkidle", timeout=15000)
                
                # Fetch full HTML
                html_content = await page.content()
                
                # Stream raw HTML to R2
                html_bytes = html_content.encode('utf-8')
                html_filename = f"html_dump_{uuid.uuid4().hex[:6]}.html"
                await self._async_upload_to_r2(html_bytes, html_filename, r2_prefix=r2_prefix, content_type="text/html")
                
                # Recursive "Bloodhound" Logic: Look for internal high-value links
                soup = BeautifulSoup(html_content, 'html.parser')
                base_domain = urlparse(url).netloc
                
                # Default bloodhound keywords + injected extract_targets
                bloodhound_keywords = ['price', 'api', 'doc', 'team', 'about']
                if extract_targets:
                    bloodhound_keywords.extend([str(t).lower() for t in extract_targets])
                
                for a_tag in soup.find_all('a', href=True):
                    href = a_tag['href']
                    full_link = urljoin(url, href)
                    link_domain = urlparse(full_link).netloc
                    
                    # Only chase internal links and specific high-value targets
                    if base_domain in link_domain:
                        if any(term in full_link.lower() for term in bloodhound_keywords):
                            if full_link not in self.visited_urls:
                                # Add to the queue dynamically
                                await queue.put(full_link)
                                logger.info(f"Bloodhound spotted high-value path: {full_link}")

            except Exception as e:
                logger.error(f"Failed to process {url}: {e}")
            finally:
                await page.close()

    async def swarming_attack(self, initial_targets: List[str], r2_prefix: str = "hunter_dump", extract_targets: List[str] = None):
        """
        Orchestrates massive parallel execution against targets.
        """
        logger.info(f"Initiating HunterSwarm Attack on {len(initial_targets)} targets...")
        self.visited_urls.clear()
        
        queue = asyncio.Queue()
        for target in initial_targets:
            await queue.put(target)

        async with async_playwright() as p:
            # We use Chromium for maximum compatibility during aggressive scraping
            browser = await p.chromium.launch(headless=True)
            # Create a shared context to save memory across the swarm
            context = await browser.new_context()

            # Worker function to consume from the queue
            async def worker():
                while True:
                    try:
                        # Wait for a URL, but timeout if the queue is empty for too long
                        url = await asyncio.wait_for(queue.get(), timeout=5.0)
                        try:
                            await self._process_target(url, context, queue, r2_prefix, extract_targets)
                        finally:
                            queue.task_done()
                    except asyncio.TimeoutError:
                        break # Queue is empty and nothing hasn't been added in 5 seconds
                    except Exception as e:
                        logger.error(f"Worker error: {e}")

            # Spawn a squad of workers based on our max_concurrent limit
            workers = [asyncio.create_task(worker()) for _ in range(self.max_concurrent)]
            
            # Wait for all workers to finish their queues
            await asyncio.gather(*workers)
            
            await context.close()
            await browser.close()
            
        logger.info(f"HunterSwarm Attack Complete. Visited {len(self.visited_urls)} unique URLs.")
        return list(self.visited_urls)

hunter_swarm = HunterSwarm(max_concurrent=10)
