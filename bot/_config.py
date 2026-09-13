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


class ActionsConfig(CustomBase):
    """Actions performed by the process."""

    send_email: bool
    """
    If enabled, the bot will send the generated e-mails.
    
    If disabled, all generated e-mails will only be stored
    as drafts in Outlook.
    """


class WorkItemsConfig(CustomBase):
    """Configuration options related to work-item creation."""

    max_cnt: int | None = None
    """Maximum amount of work items created by the producer."""


class ReportConfig(CustomBase):
    """Configuration options for the process report."""

    recipients: list[str]
    """List of e-mail addresses receiving the process report."""

    contact: str
    """Contact e-mail at Aconio for any inquiries."""


class Config(CustomBase):
    """Process Configurations"""

    actions: ActionsConfig
    work_items: WorkItemsConfig = WorkItemsConfig()
    report: ReportConfig

    def dump(self) -> None:
        """Print the loaded configuration."""
        yaml.dump(self.model_dump(exclude_unset=True), sys.stdout)
