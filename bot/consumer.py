"""Functions utilized by the consumer process."""

import functools

from aconio.core import decorators

from bot import _items, _config


@functools.lru_cache
def config() -> _config.ConsumerConfig:
    return _config.ConsumerConfig()


def setup() -> None:
    """Setup consumer process."""
    pass


def teardown() -> None:
    """Teardown consumer process."""
    pass


@decorators.attach_reporter
@decorators.run_function
def run(item: _items.Item):
    """Processes a single work item."""
    pass
