from datetime import date

from tender_scout.digest import render_digest
from tender_scout.notice import Notice
from tender_scout.scoring import ScoredNotice


def _notice(**overrides) -> Notice:
    fields = dict(
        id="1",
        title="Seabed survey framework",
        buyer_country="NL",
        notice_text="...",
        cpv_codes=["71351000"],
        publication_date=date(2026, 9, 8),
        ted_url="https://ted.europa.eu/notice/1",
    )
    fields.update(overrides)

    return Notice(**fields)


def _scored(score: int = 60, rationale: str = "...", **overrides) -> ScoredNotice:
    fields = dict(notice=_notice(**overrides), score=score, rationale=rationale)

    return ScoredNotice(**fields)


def test_renders_each_notice_with_score_and_rationale() -> None:
    scored = [
        _scored(
            score=90,
            rationale="fake rationale",
            title="Alpha",
            ted_url="https://ted.europa.eu/notice/1",
        )
    ]

    digest = render_digest(scored)

    assert "Alpha" in digest
    assert "NL" in digest
    assert "https://ted.europa.eu/notice/1" in digest
    assert "\n- Buyer country: NL\n" in digest
    assert "\n- Score: 90\n" in digest
    assert "\n- Rationale: fake rationale\n" in digest


def test_renders_a_no_matches_body_when_empty() -> None:
    digest = render_digest([])

    assert "# Tender digest\n\nNo matching notices" in digest
