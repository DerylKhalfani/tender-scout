from datetime import date, timedelta
from pathlib import Path

from tender_scout.config import Config
from tender_scout.digest import render_digest
from tender_scout.ted import TedClient
from tender_scout.filters import filter_notices
from tender_scout.scoring import score_notices, select_for_digest, Scorer
from tender_scout.seen import SeenStore


def run(config: Config, ted_client: TedClient, scorer: Scorer, store: SeenStore, today: date,
        digest_path: Path = Path("digest.md")) -> str:

    start = today - timedelta(days=7)

    notices = ted_client.fetch_notices(start, today)

    seen_ids = store.seen([n.id for n in notices])

    filtered_notices = filter_notices(notices, config, seen_ids)

    scored_notices = score_notices(filtered_notices, config, scorer)

    store.mark_seen([n.notice.id for n in scored_notices])

    filtered_scored_notices = select_for_digest(scored_notices, config)

    text = render_digest(filtered_scored_notices)

    digest_path.write_text(text, encoding="utf-8")

    return text