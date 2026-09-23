
from datetime import date
from typing import Protocol

from tender_scout.config import ALPHA3_TO_ALPHA2, COUNTRY_ALPHA3, Config
from tender_scout.notice import Notice

# The seven TED fields we ask for. Sending an unsupported name makes TED
# reply with a list of all 1830 valid ones, so keep this exact.
FIELDS = [
    "publication-number",
    "notice-title",
    "buyer-country",
    "description-lot",
    "classification-cpv",
    "publication-date",
    "links",
]

SEARCH_URL = "https://api.ted.europa.eu/v3/notices/search"
PAGE_LIMIT = 250


class TedClient(Protocol):
    def fetch_notices(self, start: date, end: date) -> list[Notice]: ...


class PlaceholderTedClient:
    """Stand-in until the real TED client (ticket 07). Fetches nothing."""

    def fetch_notices(self, start: date, end: date) -> list[Notice]:
        return []


class TedError(Exception):
    """TED was unreachable, refused the query, or returned a partial result."""


def _pick_language(by_language: dict):
    """TED keys text by language. Prefer English; 72 of 81 notices have none."""
    # TODO: return the "eng" value if present, else any value.
    # next(iter(d.values())) gives you the first value of a dict.

    for d in by_language:
        if d.lower() == "eng":

            return by_language[d]

    return next(iter(by_language.values()))


def to_notice(raw: dict) -> Notice:
    """
    Turn one raw TED record into a Notice.

    example:
    
    """
    # TODO title:       raw["notice-title"] is {"eng": "...", "hun": "..."}
    # TODO country:     raw["buyer-country"] is a LIST like ["DEU"] -> first item -> ALPHA3_TO_ALPHA2
    # TODO text:        raw["description-lot"] is {"deu": ["para", "para"]} -> pick language, then join the list
    # TODO cpv:         raw["classification-cpv"] has duplicates -> list(dict.fromkeys(...))
    # TODO date:        raw["publication-date"] is "2026-09-16+02:00" -> slice [:10], then okdate.fromisoformat
    # TODO url:         raw["links"]["html"]["ENG"]
    return Notice(
        id=raw["publication-number"],
        title=_pick_language(raw["notice-title"]),
        buyer_country=ALPHA3_TO_ALPHA2[raw["buyer-country"][0]],
        notice_text=" ".join(_pick_language(raw["description-lot"])),
        cpv_codes=list(dict.fromkeys(raw["classification-cpv"])),
        publication_date=date.fromisoformat(raw["publication-date"][:10]),
        ted_url=raw["links"]["html"]["ENG"],
    )


def _build_query(config: Config, start: date, end: date) -> str:
    """TED's expert-search syntax. Dates are YYYYMMDD with no dashes."""
    # TODO: four clauses joined by " AND ":
    #   publication-date>=<start as YYYYMMDD>
    #   publication-date<=<end as YYYYMMDD>
    #   classification-cpv IN (<config codes, space separated>)
    #   buyer-country IN (<config countries mapped through COUNTRY_ALPHA3, space separated>)
    # start.strftime("%Y%m%d") gives the date format. " ".join(...) builds the lists.

    start_date = start.strftime("%Y%m%d")
    end_date = end.strftime("%Y%m%d")

    cpv_codes = " ".join(config.cpv_codes)
    countries = [COUNTRY_ALPHA3[country] for country in config.countries]
    joined_countries = " ".join(countries)

    return (
        f"publication-date>={start_date}"
        f" AND publication-date<={end_date}" 
        f" AND classification-cpv IN ({cpv_codes})"
        f" AND buyer-country IN ({joined_countries})"
    )
           


class TedApiClient:
    """Fetches real notices from TED. `post` takes a payload dict, returns the parsed JSON."""

    def __init__(self, config: Config, post):
        self.config = config
        self.post = post

    def fetch_notices(self, start: date, end: date) -> list[Notice]:
        # TODO 1: build the payload dict: query, fields, limit, page
        #         keys are "query", "fields", "limit", "page"
        # TODO 2: call self.post(payload), wrap it in try/except and re-raise as TedError
        # TODO 3: if response["timedOut"] is true, raise TedError - the result is incomplete
        # TODO 4: if response["totalNoticeCount"] > len(response["notices"]), raise TedError
        #         one page holds 250 and a real window is ~75, so this should never fire.
        #         If it does, you need pagination and you want to know, not lose tenders.
        # TODO 5: return [to_notice(raw) for raw in response["notices"]]
        payload = {
            "query": _build_query(self.config, start, end),
            "fields": FIELDS,
            "limit": PAGE_LIMIT,
            "page": 1,
        }

        try:
            response = self.post(payload)
        except Exception as err:
            raise TedError(err) from err
        
        if response["timedOut"]:
            raise TedError("Timed Out")
        
        elif response["totalNoticeCount"] > len(response["notices"]):
            raise TedError("Notice Count is larger than the number of notices")

        return [to_notice(raw) for raw in response["notices"]]

        