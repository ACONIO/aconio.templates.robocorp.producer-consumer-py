"""This file contains functions utilized by the consumer."""
from robocorp import log, workitems

from bot.core import contexts, decorators


# @decorators.attach_reporter
@decorators.run_function
def run(ctx: contexts.RunContextConsumer, item: workitems.Input):
    """Processes one work item."""
    pass
