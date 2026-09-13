"""Errors for `aconio.dvo` module."""


class DVOError(Exception):
    """DVO related error."""


class DVOForwardTaskError(Exception):
    """The DVO task could not be forwarded to another employee."""
