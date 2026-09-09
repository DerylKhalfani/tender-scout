from pathlib import Path

import pytest

from tender_scout.config import ConfigError, EU_COUNTRIES, load_config

def test_optional_fields_get_defaults(tmp_path: Path) -> None:
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        'cpv_codes: ["71351000"]\n'
        'company_profile: "we survey things"\n'
    )

    config = load_config(config_file)

    assert config.countries == EU_COUNTRIES
    assert config.min_score == 60
    assert config.model == "gpt-5-mini"


def test_missing_file_raises_config_error(tmp_path: Path) -> None:
    missing = tmp_path / "nope.yaml"

    with pytest.raises(ConfigError):
        load_config(missing)