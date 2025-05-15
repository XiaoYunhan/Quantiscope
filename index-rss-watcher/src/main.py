import asyncio, logging, sys
from .store import EntryStore
from .watcher import FeedWatcher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

if __name__ == "__main__":
    store   = EntryStore("rss_state.db")
    watcher = FeedWatcher(store)
    asyncio.run(watcher.run_forever())
