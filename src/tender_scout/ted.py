from datetime import date
from typing import Protocol

from tender_scout.notice import Notice


class TedClient(Protocol):
    def fetch_notices(self, start: date, end: date) -> list[Notice]: ...


class PlaceholderTedClient:
    """Stand-in until the real TED client (ticket 07). Fetches nothing."""

    def fetch_notices(self, start: date, end: date) -> list[Notice]:
        return []
