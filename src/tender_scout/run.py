from datetime import date, timedelta
from pathlib import Path

from tender_scout.config import Config
from tender_scout.digest import render_digest
from tender_scout.ted import TedClient


def run(config: Config, ted_client: TedClient, today: date,
        digest_path: Path = Path("digest.md")) -> str:

    start = today - timedelta(days=7)

    notices = ted_client.fetch_notices(start, today)

    text = render_digest(notices)

    digest_path.write_text(text, encoding="utf-8")

    return text