from datetime import date
from pathlib import Path

from tender_scout.config import Config
from tender_scout.notice import Notice
from tender_scout.run import run

def _config(**overrides) -> Config:
    fields = dict(cpv_codes=["71351000"], company_profile="we survey the seabed")
    fields.update(overrides)

    return Config(**fields)


def _notice(**overrides) -> Notice:
    fields = dict(
        id="1",
        title="Seabed survey", 
        buyer_country="NL",
        notice_text="...",
        cpv_codes=["71351000"],
        publication_date=date(2026, 9, 8),
        ted_url="https://ted.europa.eu/notice/1"
        )

    fields.update(overrides)
    return Notice(**fields)


class FakeTedClient:
    def __init__(self, notices: list[Notice]) -> None:
        self.notices = notices
        self.calls: list[tuple[date, date]] = []

    def fetch_notices(self, start: date, end: date) -> list[Notice]:
        self.calls.append((start, end))
        return self.notices


def test_writes_every_notice_to_digest(tmp_path: Path) -> None:
    notices = [
        _notice(id="a", title="Alpha",
                ted_url="https://ted.europa.eu/notice/a"),
        _notice(id="b", title="Beta",
                ted_url="https://ted.europa.eu/notice/b"),
    ]

    client = FakeTedClient(notices)
    digest_path = tmp_path / "digest.md"

    text = run(_config(), client, date(2026, 9, 10), digest_path)

    written = digest_path.read_text()

    assert "Alpha" in written
    assert "Beta" in written
    assert written == text


def test_fetches_a_7_window_ending_today(tmp_path: Path) -> None:
    client = FakeTedClient([])

    run(_config(), client, date(2026, 9, 10), tmp_path / "digest.md")

    assert client.calls == [(date(2026, 9, 3), date(2026, 9, 10))]
