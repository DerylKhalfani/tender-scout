from tender_scout.seen import SeenStore
from pathlib import Path

def test_fresh_store_has_seen_nothing(tmp_path: Path) -> None:
    db_path = tmp_path / "seen.db"
    store = SeenStore(db_path)

    seen_ids = store.already_seen(["a", "b"])

    assert seen_ids == set()


def test_seen_ids_survive_a_new_store(tmp_path: Path) -> None:
    db_path = tmp_path / "seen.db"
    store_one = SeenStore(db_path)
    store_one.mark_seen(["a"])

    store_two = SeenStore(db_path)

    assert store_two.already_seen(["a", "b"]) == {"a"}


def test_seen_returns_only_recorded_ids(tmp_path: Path) -> None:
    db_path = tmp_path / "seen.db"
    store = SeenStore(db_path)

    store.mark_seen(["a", "z"])

    assert store.already_seen(["a", "b"]) == {"a"}


def test_seen_with_no_ids_returns_empty_set(tmp_path: Path) -> None:
    db_path = tmp_path / "seen.db"
    store = SeenStore(db_path)

    store.mark_seen(["a", "z"])

    assert store.already_seen([]) == set()
