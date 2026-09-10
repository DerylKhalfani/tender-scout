from datetime import date

from tender_scout.digest import render_digest
from tender_scout.notice import Notice


def _notice(**overrides) -> Notice:
    fields = dict(
        id="1",
        title="Seabed survey framework",
        buyer_country="NL",
        notice_text="...",
        cpv_codes=["71351000"],
        publication_date=date(2026, 9, 8),
        ted_url="https://ted.europa.eu/notice/1"
    )
    fields.update(overrides)

    return Notice(**fields)


def test_renders_each_notice_with_title_country_and_url() -> None:
    notices = [_notice(title="Alpha",
                       ted_url="https://ted.europa.eu/notice/1")]

    digest = render_digest(notices)

    assert "Alpha" in digest
    assert "NL" in digest
    assert "https://ted.europa.eu/notice/1" in digest
    assert "\n- Buyer country: NL\n" in digest