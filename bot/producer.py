"""Functions utilized by the producer process."""

import functools

from robocorp import log

from bot import _items, _config


@functools.lru_cache
def config() -> _config.ProducerConfig:
    return _config.ProducerConfig()


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

    if config().max_work_items:
        log.warn(
            "Max work items set - only creating "
            f"{config().max_work_items} work items!"
        )
        return work_items[: int(config().max_work_items)]
    else:
        return work_items
