"""Consumer core logic."""

import aconio.decorators

import bot._items as _items


def setup() -> None:
    """Setup consumer process."""
    pass


def teardown() -> None:
    """Teardown consumer process."""
    pass


@aconio.decorators.attach_reporter
@aconio.decorators.run_function
def run(item: _items.Item):
    """Processes a single work item."""
    print(item)
