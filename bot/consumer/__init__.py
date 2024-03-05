"""This file contains functions utilized by the consumer."""
from robocorp import log, workitems

from bot.core import tools, context


# @tools.attach_reporter
@tools.run_function
def run(ctx: context.RunContextConsumer, item: workitems.Input):
    """Processes one work item."""
    pass
