import json
from pathlib import Path


class SeenStore:
    def __init__(self, json_path: Path):
        self.json_path = json_path


    def _load(self) -> set[str]:
        """Every id on record. A missing file means nothing has been seen yet."""
        if not self.json_path.exists():
            return set()

        return set(json.loads(self.json_path.read_text()))

    def mark_seen(self, ids: list[str]) -> None:
        """
        Record notice ids as reported, so future runs skip them.
        Safe to call with ids already recorded
        """

        set_of_ids = self._load()

        set_of_ids.update(ids)

        sorted_ids = json.dumps(sorted(set_of_ids))
        self.json_path.write_text(sorted_ids)

        
    def already_seen(self, ids: list[str]) -> set[str]:
        """
        Return the ids among the given ones that were already reported.
        Ids this store has no record of are left out; an empty input
        returns an empty set.
        """

        set_of_ids = self._load()
        intersection_ids = set_of_ids.intersection(ids)

        return intersection_ids

