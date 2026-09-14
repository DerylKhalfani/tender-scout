from datetime import date
from pathlib import Path

from tender_scout.config import Config
from tender_scout.notice import Notice
from tender_scout.scoring import ScoredNotice
from tender_scout.run import run
from tender_scout.filters import matches

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


class FakeScorer:
    def __init__(self, scores: dict[str, int]) -> None:
        self.scores = scores

    def score(self, notice: Notice, config: Config) -> tuple[int, str]:
        notice_id_score = self.scores[notice.id]

        return notice_id_score, f"Fake scorer output {notice.id}"


def test_writes_every_notice_to_digest(tmp_path: Path) -> None:
    notices = [
        _notice(id="a", title="Alpha",
                ted_url="https://ted.europa.eu/notice/a"),
        _notice(id="b", title="Beta",
                ted_url="https://ted.europa.eu/notice/b"),
    ]

    client = FakeTedClient(notices)
    scorer = FakeScorer({"a": 90, "b": 70})
    digest_path = tmp_path / "digest.md"

    text = run(_config(), client, scorer, date(2026, 9, 10), digest_path)

    written = digest_path.read_text()

    assert "Alpha" in written
    assert "Beta" in written
    assert written == text


def test_fetches_a_7_window_ending_today(tmp_path: Path) -> None:
    client = FakeTedClient([])
    scorer = FakeScorer({})


    run(_config(), client, scorer, date(2026, 9, 10), tmp_path / "digest.md")

    assert client.calls == [(date(2026, 9, 3), date(2026, 9, 10))]


def test_only_matching_notices_reach_the_digest(tmp_path: Path) -> None:
    notices = [
        _notice(id="a", title="Alpha",
                        ted_url="https://ted.europa.eu/notice/a"),
        _notice(id="b", title="Beta", 
                        cpv_codes=["71371000"],
                        ted_url="https://ted.europa.eu/notice/b"),
        _notice(id="c", title="Charlie", 
                        buyer_country="NL", 
                        cpv_codes=["71351000", "71361000"],
                        ted_url="https://ted.europa.eu/notice/c"),
        _notice(id="d", title="Delta", buyer_country="US",
                        ted_url="https://ted.europa.eu/notice/d"),
    ]

    client = FakeTedClient(notices)
    scorer = FakeScorer({"a": 90, "b": 70, "c": 60, "d": 60})
    digest_path = tmp_path / "digest.md"

    text = run(_config(), client, scorer, date(2026, 9, 10), digest_path)
    
    written = digest_path.read_text()

    assert "Alpha" in written
    assert "Beta" not in written
    assert "Charlie" in written
    assert "Delta" not in written

    assert written == text


def test_drops_low_scores_and_sorts_by_score(tmp_path: Path) -> None:
    notices = [
            _notice(id="a", title="Alpha",
                            ted_url="https://ted.europa.eu/notice/a"),
            _notice(id="b", title="Beta",
                            ted_url="https://ted.europa.eu/notice/b"),
            _notice(id="c", title="Charlie", 
                            ted_url="https://ted.europa.eu/notice/c"),
            _notice(id="d", title="Delta",
                            ted_url="https://ted.europa.eu/notice/d"),
        ]
    client = FakeTedClient(notices)
    scorer = FakeScorer({"a": 90, "b": 70, "c": 30, "d": 60})
    digest_path = tmp_path / "digest.md"

    text = run(_config(), client, scorer, date(2026, 9, 10), digest_path)

    written = digest_path.read_text()

    assert "Alpha" in written
    assert "Beta" in written
    assert "Charlie" not in written
    assert "Delta" in written
    assert written.index("Alpha") < written.index("Beta")
    assert written == text


def test_writes_no_matches_body_when_nothing_clears_threshold(tmp_path: Path) -> None:
    notices = [
                _notice(id="a", title="Alpha",
                                ted_url="https://ted.europa.eu/notice/a"),
                _notice(id="b", title="Beta",
                                ted_url="https://ted.europa.eu/notice/b"),
                _notice(id="c", title="Charlie", 
                                ted_url="https://ted.europa.eu/notice/c"),
                _notice(id="d", title="Delta",
                                ted_url="https://ted.europa.eu/notice/d"),
            ]
    client = FakeTedClient(notices)
    scorer = FakeScorer({"a": 50, "b": 50, "c": 30, "d": 50})
    digest_path = tmp_path / "digest.md"

    text = run(_config(), client, scorer, date(2026, 9, 10), digest_path)

    written = digest_path.read_text()

    assert "No matching notices" in text
    assert written == text
