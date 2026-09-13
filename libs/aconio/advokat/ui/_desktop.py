"""Provide a cached instance of `RPA.Desktop.Desktop`."""

import functools

import RPA.Desktop


@functools.lru_cache
def desktop() -> RPA.Desktop.Desktop:
    return RPA.Desktop.Desktop()
