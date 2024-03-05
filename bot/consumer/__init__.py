"""This file contains functions utilized by the consumer."""
from robocorp import log, workitems

from bot.core import decorators, context


# @decorators.attach_reporter
@decorators.run_function
def run(ctx: context.RunContextConsumer, item: workitems.Input):
    """Processes one work item."""
    pass
