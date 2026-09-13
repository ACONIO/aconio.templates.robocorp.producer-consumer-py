"""Robot test cases."""

import faulthandler

import robocorp.tasks

faulthandler.disable()


@robocorp.tasks.task
def test_generic() -> None:
    """Template for quickly testing throughout the development process."""
    pass
