"""Producer core logic."""

import robocorp.log

import bot._items as _items
import bot._config as _config


def setup() -> None:
    """Setup producer process."""
    pass


def teardown() -> None:
    """Teardown producer process."""
    pass


def run() -> list[_items.Item]:
    """Generate a list of work items."""

    work_items = []

    # TODO: Implement producer

    if max_work_items := _config.config().work_items.max_cnt:
        robocorp.log.warn(
            f"Max work items set - only creating {max_work_items} work items!"
        )
        return work_items[:max_work_items]
    else:
        return work_items
