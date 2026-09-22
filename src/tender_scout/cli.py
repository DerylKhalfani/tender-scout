import sys
import argparse
import traceback
from pathlib import Path
from datetime import date

from tender_scout.config import ConfigError, load_config
from tender_scout.run import run
from tender_scout.scoring import PlaceholderScorer
from tender_scout.ted import PlaceholderTedClient
from tender_scout.seen import SeenStore

CONFIG_PATH = Path("config.yaml")

def main() -> None:
    parser = argparse.ArgumentParser(prog="tender-scout")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config.yaml"),
        help="path to config.yaml (default: ./config.yaml)"
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
        digest = run(config, PlaceholderTedClient(), PlaceholderScorer(), SeenStore(Path("seen.db")), date.today())

    except Exception as err:
        print(f"run did not complete: {err}", file=sys.stderr)
        print("digest.md may be missing or stale", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)
        
    print(f"wrote digest.md ({len(digest.splitlines())} lines)")