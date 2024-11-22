"""Robot configuration management."""

import os
import sys
import yaml
import pydantic

import functools

from aconio.core import errors

_config_path = None


class CustomBase(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        extra="forbid", use_enum_values=True, arbitrary_types_allowed=True
    )
    model_config = pydantic.ConfigDict(coerce_numbers_to_str=True)


class Config(CustomBase):
    """Process Configurations"""

    # TODO Create config
    pass


def set_config_path(path: str) -> None:
    """Set the path to the configuration file.

    Args:
        path:
            The path to the `.yaml` configuration file.
    """
    globals()["_config_path"] = path


@functools.lru_cache
def config() -> Config:
    with open(_config_path, encoding="UTF-8") as stream:
        try:
            data = yaml.safe_load(stream)
            return Config(**data)
        except yaml.YAMLError as exc:
            raise errors.ApplicationError(
                "Failed to load YAML config!"
            ) from exc


def dump() -> None:
    """Print the configuration."""
    yaml.dump(config().model_dump(exclude_unset=True), sys.stdout)


def env() -> str:
    """Return the execution environment ("dev" | "test" | "prod")."""
    return os.environ.get("ENVIRONMENT").lower()
