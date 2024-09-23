"""Robot configuration management."""

import os
import sys
import yaml
import pydantic


class BaseConfig(pydantic.BaseModel):
    """Shared configuration."""

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    pass


class ProducerConfig(BaseConfig):
    """Producer configuration."""

    max_work_items: int | None = os.environ.get("MAX_WORK_ITEMS")
    """Maximum amount of work items created by the Producer."""


class ConsumerConfig(BaseConfig):
    """Consumer configuration."""

    # The != "false" condition prevents the test mode from accidentally being
    # turned off, for example through a typo. Everything which is not
    # "false" will resolve to "true" and thus enable the test mode.
    test_mode: bool = os.environ.get("TEST_MODE", "true").lower() != "false"
    """
    If enabled, the bot does not perform any "critical" actions, such as
    sending e-mails, or inserting data in applications.
    Per default, test mode is enabled.
    """


class ReporterConfig(BaseConfig):
    """Reporter configuration."""

    # The != "false" condition prevents the test mode from accidentally being
    # turned off, for example through a typo. Everything which is not
    # "false" will resolve to "true" and thus enable the test mode.
    test_mode: bool = os.environ.get("TEST_MODE", "true").lower() != "false"
    """
    If enabled, report e-mail will only be stored as draft.
    Per default, test mode is enabled.
    """

    recipients: str = os.environ.get("RECIPIENT")
    """E-Mail or list of semicolon-separated e-mails of report recipients."""

    contact: str = os.environ.get("CONTACT")
    """Contact person at Aconio."""


def dump(config: BaseConfig) -> None:
    """Print the configuration."""
    yaml.dump(config.model_dump(exclude_unset=True), sys.stdout)
