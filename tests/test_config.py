from pathlib import Path

import pytest

from tender_scout.config import EU_COUNTRIES, ConfigError, load_config


def test_optional_fields_get_defaults(tmp_path: Path) -> None:
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        'cpv_codes: ["71351000"]\ncompany_profile: "we survey things"\n'
    )

    config = load_config(config_file)

    assert config.countries == EU_COUNTRIES
    assert config.min_score == 60
    assert config.model == "gpt-5-mini"


def test_missing_file_raises_config_error(tmp_path: Path) -> None:
    missing = tmp_path / "nope.yaml"

    with pytest.raises(ConfigError):
        load_config(missing)


def test_unknown_key_raises(tmp_path: Path) -> None:
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        'cpv_codes: ["71351000"]\ncompany_profile: "x"\nmin_scor: 50\n'
    )

    with pytest.raises(ConfigError):
        load_config(config_file)


def test_directory_instead_of_file_raises(tmp_path: Path) -> None:
    with pytest.raises(ConfigError):
        load_config(tmp_path)


@pytest.mark.parametrize("bad", ["-5", "0", "150", "true"])
def test_out_of_range_min_score_raises(tmp_path: Path, bad: str) -> None:
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        f'cpv_codes: ["71351000"]\ncompany_profile: "x"\nmin_score: {bad}\n'
    )
    with pytest.raises(ConfigError):
        load_config(config_file)
