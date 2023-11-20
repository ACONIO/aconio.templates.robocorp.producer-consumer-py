"""This file contains functions utilized by the consumer."""

from robocorp import log
from robocorp.workitems import Input

from .internal.tools import run_function
from .internal.context import RunContextConsumer


@run_function
def run(ctx: RunContextConsumer, item: Input):
    """Processes one work item."""
    pass
