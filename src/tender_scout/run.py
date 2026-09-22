from datetime import date, timedelta
from pathlib import Path

from tender_scout.config import Config
from tender_scout.digest import render_digest
from tender_scout.filters import filter_notices
from tender_scout.scoring import Scorer, score_notices, select_for_digest
from tender_scout.seen import SeenStore
from tender_scout.ted import TedClient


def run(
    config: Config,
    ted_client: TedClient,
    scorer: Scorer,
    store: SeenStore,
    today: date,
    digest_path: Path = Path("digest.md"),
) -> str:

    start = today - timedelta(days=7)

    notices = ted_client.fetch_notices(start, today)

    seen_ids = store.already_seen([n.id for n in notices])

    filtered_notices = filter_notices(notices, config)

    unseen_notices = [n for n in filtered_notices if n.id not in seen_ids]

    scored_notices = score_notices(unseen_notices, config, scorer)

    digest_notices = select_for_digest(scored_notices, config)

    text = render_digest(digest_notices)

    digest_path.write_text(text, encoding="utf-8")

    store.mark_seen([n.notice.id for n in scored_notices])

    return text
