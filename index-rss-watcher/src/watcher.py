import asyncio, re, aiohttp, feedparser, logging, csv, os
from typing import Optional, List, Set
from datetime import datetime
from .config import FEED_URL, POLL_INTERVAL_SEC
from .notifier import Notifier

log = logging.getLogger("watcher")

# Simple pattern to find "replace" in description
REPLACE_PATTERN = re.compile(r"replac", re.I)

class FeedWatcher:
    def __init__(self):
        self.etag: Optional[str] = None
        self.modified: Optional[str] = None
        self.csv_path = "data/seen_entries.csv"
        self.seen_ids: Set[str] = self._load_seen_entries()
        
    def _load_seen_entries(self) -> Set[str]:
        """Load previously seen entry IDs from CSV"""
        seen = set()
        if os.path.exists(self.csv_path):
            try:
                with open(self.csv_path, 'r', newline='') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        seen.add(row['entry_id'])
                log.info(f"Loaded {len(seen)} previously seen entries")
            except Exception as e:
                log.error(f"Error loading CSV: {e}")
        return seen
    
    def _save_entry(self, entry_id: str, title: str, link: str) -> None:
        """Save a new entry to CSV"""
        file_exists = os.path.exists(self.csv_path)
        
        with open(self.csv_path, 'a', newline='') as f:
            fieldnames = ['timestamp', 'entry_id', 'title', 'link']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow({
                'timestamp': datetime.now().isoformat(),
                'entry_id': entry_id,
                'title': title,
                'link': link
            })
        
        self.seen_ids.add(entry_id)
        
    async def test_feed_access(self) -> bool:
        """Test if RSS feed is accessible"""
        async with aiohttp.ClientSession() as session:
            try:
                data = await self._fetch(session)
                return len(data) > 0
            except Exception as e:
                log.error(f"Feed access test failed: {e}")
                return False

    async def _fetch(self, session: aiohttp.ClientSession) -> bytes:
        # Use the working headers based on your test results
        hdrs = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
        if self.etag:      hdrs["If-None-Match"]   = self.etag
        if self.modified:  hdrs["If-Modified-Since"] = self.modified
        
        # Focus on the single working URL based on your test
        url = FEED_URL
        
        try:
            async with session.get(url, headers=hdrs, timeout=30) as resp:
                log.info(f"Fetching RSS from: {url} - Status: {resp.status}")
                
                if resp.status == 304:  # No new content
                    log.info("No new content (304 Not Modified)")
                    return b""
                elif resp.status == 200:
                    self.etag     = resp.headers.get("ETag", self.etag)
                    self.modified = resp.headers.get("Last-Modified", self.modified)
                    data = await resp.read()
                    log.info(f"Successfully fetched RSS feed, {len(data)} bytes")
                    return data
                elif resp.status == 403:
                    log.error(f"Access denied (403) to {url} - check robots.txt compliance")
                    raise Exception(f"RSS feed access denied: {resp.status}")
                else:
                    log.error(f"HTTP {resp.status} from {url}")
                    raise Exception(f"RSS feed error: HTTP {resp.status}")
                    
        except Exception as e:
            log.error(f"Failed to fetch RSS feed: {e}")
            raise

    async def run_forever(self):
        log.info(f"Starting RSS watcher with {POLL_INTERVAL_SEC}s interval")
        
        # Use session with connection pooling and retry logic
        connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
        timeout = aiohttp.ClientTimeout(total=60, connect=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            consecutive_errors = 0
            max_errors = 5
            
            while True:
                try:
                    start_time = asyncio.get_event_loop().time()
                    data = await self._fetch(session)
                    
                    if data:
                        self._process_feed(data)
                        consecutive_errors = 0
                    else:
                        log.info("No new content (304 Not Modified)")
                        
                    fetch_time = asyncio.get_event_loop().time() - start_time
                    log.info(f"Fetch completed in {fetch_time:.2f}s")
                    
                except Exception as e:
                    consecutive_errors += 1
                    log.exception(f"Fetch error ({consecutive_errors}/{max_errors}): %s", e)
                    
                    if consecutive_errors >= max_errors:
                        log.error(f"Too many consecutive errors ({max_errors}), waiting longer...")
                        await asyncio.sleep(POLL_INTERVAL_SEC * 3)
                        consecutive_errors = 0
                
                await asyncio.sleep(POLL_INTERVAL_SEC)

    def _process_feed(self, raw: bytes):
        feed = feedparser.parse(raw)
        log.info(f"Processing feed with {len(feed.entries)} entries")
        
        for entry in feed.entries:
            entry_id = getattr(entry, 'id', entry.link)
            if entry_id in self.seen_ids:
                continue
                
            # Check if description contains "replace"
            description = getattr(entry, 'description', '')
            
            if REPLACE_PATTERN.search(description):
                # Send the entire item content
                title = getattr(entry, 'title', 'No title')
                published = getattr(entry, 'published', 'Unknown date')
                link = getattr(entry, 'link', '')
                
                # Send full item details
                text = f"🚨 Index Change Alert\n\n" \
                       f"Title: {title}\n\n" \
                       f"Published: {published}\n\n" \
                       f"Description:\n{description}\n\n" \
                       f"Link: {link}"
                
                try:
                    success = Notifier.send(text)
                    if success:
                        log.info("Notified: %s", title)
                    else:
                        log.error("Failed to send notification for: %s", title)
                except Exception as e:
                    log.exception("Notify error: %s", e)
            else:
                log.debug(f"Skipping entry (no 'replace' in description): {entry.title}")
                
            self._save_entry(entry_id, entry.title, entry.link)
