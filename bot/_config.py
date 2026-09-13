"""Robot configuration management."""

from __future__ import annotations

import sys
import yaml
import pydantic

import functools

import bot._env as _env

_config = None


@functools.lru_cache
def config() -> Config:
    if _config is None:
        raise RuntimeError("Config not loaded! Call `load()` first.")
    return _config


def load() -> None:
    """Load the bot configuration.

    **Requirements**
    - The environment variable `ENVIRONMENT` must be set to one of the
    following values: [`"dev"`, `"test"`, `"prod"`].
    - In case of `"test"` or `"prod"` environment: The environment variable
    `AZURE_CONFIG_DIR` must be set to the Azure Files directory where the
    YAML config files are stored.
    """
    global _config

    with open(_env.get_yaml_config_path(), encoding="UTF-8") as stream:
        try:
            data = yaml.safe_load(stream)
            _config = Config(**data)
        except yaml.YAMLError as exc:
            raise RuntimeError("Failed to load YAML config!") from exc


class CustomBase(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        extra="forbid",
        use_enum_values=True,
        coerce_numbers_to_str=True,
        arbitrary_types_allowed=True,
    )


class Config(CustomBase):
    """Process Configurations"""

    # TODO Create config
    pass

    def dump(self) -> None:
        """Print the loaded configuration."""
        yaml.dump(self.model_dump(exclude_unset=True), sys.stdout)
