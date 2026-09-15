from tender_scout.seen import SeenStore
from pathlib import Path

def test_all_ids_are_new_in_a_fresh_store(tmp_path: Path) -> None:
    db_path = tmp_path / "seen.db"
    store = SeenStore(db_path)

    new_ids = store.unseen(["a", "b"])

    assert new_ids == ["a", "b"]


def test_marked_ids_are_no_longer_new(tmp_path: Path) -> None:
    db_path = tmp_path / "seen.db"
    store = SeenStore(db_path)

    store.mark_seen(["a"])
    new_ids = store.unseen(["a", "b"])

    assert new_ids == ["b"]


def test_seen_ids_survive_a_new_store(tmp_path: Path) -> None:
    db_path = tmp_path / "seen.db"
    store_one = SeenStore(db_path)
    store_two = SeenStore(db_path)

    store_one.mark_seen(["a"])

    assert store_two.unseen(["a", "b"]) == ["b"]
