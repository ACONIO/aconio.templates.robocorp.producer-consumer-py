"""Collection of BMD related errors."""


class BMDError(Exception):
    """BMD related error."""


class BMDUpdateDetectedError(BMDError):
    """Raised when a BMD update notification is detected."""
