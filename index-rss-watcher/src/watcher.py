import asyncio, re, aiohttp, feedparser, logging
from typing import Optional
from .config import FEED_URL, POLL_INTERVAL_SEC
from .store  import EntryStore
from .notifier import Notifier

log = logging.getLogger("watcher")

PATTERN = re.compile(r"(constituen|addition|deletion)", re.I)

class FeedWatcher:
    def __init__(self, store: EntryStore):
        self.store = store
        self.etag: Optional[str] = None
        self.modified: Optional[str] = None

    async def _fetch(self, session: aiohttp.ClientSession) -> bytes:
        hdrs = {}
        if self.etag:      hdrs["If-None-Match"]   = self.etag
        if self.modified:  hdrs["If-Modified-Since"] = self.modified
        async with session.get(FEED_URL, headers=hdrs, timeout=20) as resp:
            if resp.status == 304:  # 无新内容
                return b""
            # 保存条件头
            self.etag     = resp.headers.get("ETag", self.etag)
            self.modified = resp.headers.get("Last-Modified", self.modified)
            return await resp.read()

    async def run_forever(self):
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    data = await self._fetch(session)
                    if data:
                        self._process_feed(data)
                except Exception as e:
                    log.exception("Fetch error: %s", e)
                await asyncio.sleep(POLL_INTERVAL_SEC)

    def _process_feed(self, raw: bytes):
        feed = feedparser.parse(raw)
        for entry in feed.entries:
            if self.store.is_seen(entry.id):
                continue
            if PATTERN.search(entry.title):
                text = f"[Index Change] {entry.title}\n{entry.link}"
                try:
                    Notifier.send(text)
                    log.info("Notified: %s", entry.title)
                except Exception as e:
                    log.exception("Notify error: %s", e)
            self.store.mark_seen(entry.id)
