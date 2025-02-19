"""Simple module to manage project-wide delay times."""

import functools


class DelayManager:
    """Multiply given delays by a configured factor."""

    def __init__(self, factor: float = 1.0) -> None:
        self._factor = factor

    def set_factor(self, factor: float) -> None:
        self._factor = factor

    def get(self, wait_time: float) -> float:
        """Return the given delay time multiplied by the configured factor."""
        return wait_time * self._factor


@functools.lru_cache
def delay() -> DelayManager:
    return DelayManager()
