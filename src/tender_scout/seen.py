import sqlite3
from pathlib import Path


class SeenStore:
    def __init__(self, db_path: Path):
        self.db_path = db_path

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS seen (id TEXT PRIMARY KEY)")

    def unseen(self, ids: list[str]) -> list[str]:
        """
        Return the ids that have not been reported in a previous digest,
        in the order given
        """
        with sqlite3.connect(self.db_path) as conn:
            set_of_ids = {row[0] for row in conn.execute("SELECT id FROM seen")}

        list_of_ids = []
        for id in ids:
            if id not in set_of_ids:
                list_of_ids.append(id)

        return list_of_ids

    def mark_seen(self, ids: list[str]) -> None:
        """
        Record notice ids as reported, so future runs skip them.
        Safe to call with ids already recorded
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany("INSERT OR IGNORE INTO seen (id) VALUES (?)",
                             [(i,) for i in ids])
