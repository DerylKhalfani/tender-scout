"""Configuration for a tender-scout run"""

from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

EU_COUNTRIES: list[str] = [
    "AT",
    "BE",
    "BG",
    "HR",
    "CY",
    "CZ",
    "DK",
    "EE",
    "FI",
    "FR",
    "DE",
    "GR",
    "HU",
    "IE",
    "IT",
    "LV",
    "LT",
    "LU",
    "MT",
    "NL",
    "PL",
    "PT",
    "RO",
    "SK",
    "SI",
    "ES",
    "SE",
]

COUNTRY_ALPHA3: dict[str, str] = {
    "AT": "AUT", "BE": "BEL", "BG": "BGR", "HR": "HRV", "CY": "CYP",
    "CZ": "CZE", "DK": "DNK", "EE": "EST", "FI": "FIN", "FR": "FRA",
    "DE": "DEU", "GR": "GRC", "HU": "HUN", "IE": "IRL", "IT": "ITA",
    "LV": "LVA", "LT": "LTU", "LU": "LUX", "MT": "MLT", "NL": "NLD",
    "PL": "POL", "PT": "PRT", "RO": "ROU", "SK": "SVK", "SI": "SVN",
    "ES": "ESP", "SE": "SWE",
}

ALPHA3_TO_ALPHA2: dict[str, str] = {v: k for k, v in COUNTRY_ALPHA3.items()}


class Config(BaseModel):
    """Validated tender-scout configuration."""

    model_config = ConfigDict(extra="forbid")

    cpv_codes: list[str]
    company_profile: str
    countries: list[str] = Field(default_factory=lambda: list(EU_COUNTRIES))
    min_score: int = Field(default=60, ge=1, le=100, strict=True)
    model: str = "gpt-5-mini"


class ConfigError(Exception):
    """Raised when config.yaml is missing or malformed."""


def load_config(path: Path) -> Config:
    # reading path as text
    try:
        text = path.read_text()
    except OSError as err:
        raise ConfigError(f"config file not found: {path}: {err}") from err

    # load yaml
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as err:
        raise ConfigError(f"config file is not valid YAML: {err}") from err

    # check the mapping of the yaml
    if not isinstance(data, dict):
        raise ConfigError(
            f"config file must contain a mapping, got {type(data).__name__}"
        )

    # return a Config object
    try:
        return Config(**data)
    except ValidationError as err:
        raise ConfigError(f"config file is invalid:\n{err}") from err
