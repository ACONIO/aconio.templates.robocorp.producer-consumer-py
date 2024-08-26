"""Robot test cases."""

import faulthandler

from robocorp import tasks


faulthandler.disable()


@tasks.task
def test_generic() -> None:
    """Template for quickly testing throughout the development process."""
    pass
