import asyncio, re, aiohttp, feedparser, logging
from typing import Optional, List
from .config import FEED_URL, POLL_INTERVAL_SEC
from .store  import EntryStore
from .notifier import Notifier

log = logging.getLogger("watcher")

# Enhanced pattern for index component changes
PATTERN = re.compile(r"(constituent|addition|deletion|changes?|announced?|effective|removed?|added|replacing|replaced)", re.I)

# More specific patterns for index changes
INDEX_CHANGE_PATTERNS = [
    re.compile(r"index.*(addition|deletion|constituent|change)", re.I),
    re.compile(r"(addition|deletion).*(index|constituent)", re.I),
    re.compile(r"(s&p|dow|russell|ftse).*(change|addition|deletion|constituent)", re.I),
    re.compile(r"effective.*(addition|deletion|change)", re.I),
    re.compile(r"announced.*(addition|deletion|change)", re.I)
]

class FeedWatcher:
    def __init__(self, store: EntryStore):
        self.store = store
        self.etag: Optional[str] = None
        self.modified: Optional[str] = None
        
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
        hdrs = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        if self.etag:      hdrs["If-None-Match"]   = self.etag
        if self.modified:  hdrs["If-Modified-Since"] = self.modified
        
        # Try multiple potential RSS URLs
        urls_to_try = [
            FEED_URL,
            'https://www.spglobal.com/spdji/en/rss/rss-details/?rssFeedName=index-news-announcements.xml',
            'https://www.spglobal.com/spdji/en/rss/index-news-announcements.xml',
            'https://www.spglobal.com/spdji/en/rss/index-news-announcements',
            'https://investor.spglobal.com/feeds/rss/index-news.xml'
        ]
        
        for url in urls_to_try:
            try:
                async with session.get(url, headers=hdrs, timeout=30) as resp:
                    log.info(f"Trying URL: {url} - Status: {resp.status}")
                    if resp.status == 304:  # No new content
                        return b""
                    elif resp.status == 200:
                        self.etag     = resp.headers.get("ETag", self.etag)
                        self.modified = resp.headers.get("Last-Modified", self.modified)
                        data = await resp.read()
                        log.info(f"Successfully fetched from {url}, {len(data)} bytes")
                        return data
                    elif resp.status == 403:
                        log.warning(f"Access denied to {url}")
                        continue
                    else:
                        log.warning(f"HTTP {resp.status} for {url}")
                        continue
            except Exception as e:
                log.warning(f"Error fetching {url}: {e}")
                continue
        
        raise Exception("All RSS URLs failed")

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
            if self.store.is_seen(entry_id):
                continue
                
            # Check multiple content fields for index changes
            content_to_check = [
                getattr(entry, 'title', ''),
                getattr(entry, 'summary', ''),
                getattr(entry, 'description', '')
            ]
            
            content_text = ' '.join(content_to_check).lower()
            
            # Use enhanced pattern matching
            is_index_change = any(pattern.search(content_text) for pattern in INDEX_CHANGE_PATTERNS)
            
            if is_index_change or PATTERN.search(content_text):
                # Extract more detailed information
                summary = getattr(entry, 'summary', '')[:200] + '...' if hasattr(entry, 'summary') else ''
                published = getattr(entry, 'published', 'Unknown date')
                
                text = f"🚨 Index Change Alert\n" \
                       f"Title: {entry.title}\n" \
                       f"Published: {published}\n" \
                       f"Summary: {summary}\n" \
                       f"Link: {entry.link}"
                
                try:
                    success = Notifier.send(text)
                    if success:
                        log.info("Notified: %s", entry.title)
                    else:
                        log.error("Failed to send notification for: %s", entry.title)
                except Exception as e:
                    log.exception("Notify error: %s", e)
            else:
                log.debug(f"Skipping non-index entry: {entry.title}")
                
            self.store.mark_seen(entry_id)
