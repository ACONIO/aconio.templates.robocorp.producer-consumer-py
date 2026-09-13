"""Configuration for the USP module."""

import functools


class Config:
    """Configuration for the USP module."""

    browser_debug: bool = False
    """Toggle Playwright browser debug mode."""


@functools.lru_cache
def config() -> Config:
    """Return the USP module configuration."""
    return Config()
