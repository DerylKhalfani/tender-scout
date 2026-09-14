from datetime import date, timedelta
from pathlib import Path

from tender_scout.config import Config
from tender_scout.digest import render_digest
from tender_scout.ted import TedClient
from tender_scout.filters import filter_notices
from tender_scout.scoring import score_notices, Scorer


def run(config: Config, ted_client: TedClient, scorer: Scorer, today: date,
        digest_path: Path = Path("digest.md")) -> str:

    start = today - timedelta(days=7)

    notices = ted_client.fetch_notices(start, today)

    filtered_notices = filter_notices(notices, config)

    scored_notices = score_notices(filtered_notices, config, scorer)

    text = render_digest(scored_notices)

    digest_path.write_text(text, encoding="utf-8")

    return text