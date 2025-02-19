"""Provide a cached instance of `RPA.Desktop.Desktop`."""

import functools

from RPA.Desktop import Desktop


@functools.lru_cache
def desktop() -> Desktop:
    return Desktop()
