from datetime import date

from tender_scout.config import Config
from tender_scout.filters import matches
from tender_scout.notice import Notice

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
        ted_url="https://ted.europa.eu/notice/1",
    )
    fields.update(overrides)
    return Notice(**fields)

def test_keeps_notice_with_matching_cpv_and_country() -> None:
    assert matches(_notice(), _config()) is True


def test_drops_notice_with_wrong_cpv() -> None:
    assert matches(_notice(cpv_codes=["41500000"]), _config()) is False


def test_drops_notice_with_wrong_country() -> None:
    assert matches(_notice(buyer_country="US"), _config()) is False


def test_keeps_notice_when_one_of_several_cpv_codes_matches() -> None:
    assert matches(_notice(cpv_codes=["71351000", "41500000", "41600000"]), _config()) is True
    