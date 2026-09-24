import argparse
import sys
import traceback
from datetime import date
from pathlib import Path

import httpx

from tender_scout.config import ConfigError, load_config
from tender_scout.run import run
from tender_scout.scoring import LLMScorer
from tender_scout.seen import SeenStore
from tender_scout.ted import SEARCH_URL, TedApiClient

CONFIG_PATH = Path("config.yaml")

def post(payload: dict) -> dict:
    """Send one search request to TED and return the parsed JSON."""
    response = httpx.post(SEARCH_URL, json=payload, timeout=90)
    response.raise_for_status()
    return response.json()


def main() -> None:
    parser = argparse.ArgumentParser(prog="tender-scout")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config.yaml"),
        help="path to config.yaml (default: ./config.yaml)",
    )
    args = parser.parse_args()
    try:
        config = load_config(args.config)

    except ConfigError as err:
        print(err, file=sys.stderr)
        sys.exit(1)

    print(f"tender-scout config loaded from {args.config}")
    print(f" CPV codes:         {config.cpv_codes}")
    print(f" countries:         {len(config.countries)} ({','.join(config.countries[:5])})")
    print(f" min_score:         {config.min_score}")
    print(f" model:             {config.model}")
    print(f" company_profile:   {config.company_profile[:60]}")

    try:
        digest = run(
            config,
            TedApiClient(config, post=post),
            LLMScorer(config),
            SeenStore(Path("seen.json")),
            date.today(),
        )

    except Exception as err:  # noqa: BLE001 - top-level CLI boundary, nothing should escape
        print(f"run did not complete: {err}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)

    print(f"wrote digest.md ({len(digest.splitlines())} lines)")
