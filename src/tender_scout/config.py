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
