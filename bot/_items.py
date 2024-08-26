"""Specification of the work item passed to Robocorp Control Room."""

import pydantic


class Item(pydantic.BaseModel):
    """A work item created by the Producer and processed by the Consumer."""
    pass
