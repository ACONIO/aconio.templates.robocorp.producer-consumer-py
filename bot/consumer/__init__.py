"""This file contains functions utilized by the consumer."""
import robocorp.workitems
import robocorp.log as log

import bot.reporter # TODO: This import kinda doesn't make sense. Move attach_reporter somewhere else?
import bot.core.tools as tools
import bot.core.context as ctx


# @bot.reporter.attach_reporter
@tools.run_function
def run(ctx: ctx.RunContextConsumer, item: robocorp.workitems.Input):
    """Processes one work item."""
    pass
