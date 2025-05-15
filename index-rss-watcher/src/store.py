import sqlite3
from contextlib import contextmanager

class EntryStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        with self._conn() as cur:
            cur.execute(
                "CREATE TABLE IF NOT EXISTS seen (id TEXT PRIMARY KEY)"
            )

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn.cursor()
            conn.commit()
        finally:
            conn.close()

    def is_seen(self, entry_id: str) -> bool:
        with self._conn() as cur:
            cur.execute("SELECT 1 FROM seen WHERE id=?;", (entry_id,))
            return cur.fetchone() is not None

    def mark_seen(self, entry_id: str) -> None:
        with self._conn() as cur:
            cur.execute("INSERT OR IGNORE INTO seen (id) VALUES (?);", (entry_id,))
