import sys
from pathlib import Path
from tender_scout.config import ConfigError, load_config

CONFIG_PATH = Path("config.yaml")

def main() -> None:
    try:
        config = load_config(CONFIG_PATH)
    except ConfigError as err:
        print(err, file=sys.stderr)
        sys.exit(1)

    print(f"tender-scout config loaded from {CONFIG_PATH}")
    print(f" CPV codes:         {config.cpv_codes}")
    print(f" countries:         {len(config.countries)} ({','.join(config.countries[:5])})")
    print(f" min_score:         {config.min_score}")
    print(f" model:             {config.model}")
    print(f" company_profile:   {config.company_profile[:60]}")