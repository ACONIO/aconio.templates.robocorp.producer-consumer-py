"""This file contains functions utilized by the producer."""
from robocorp import log

from bot.core import decorators, context


@decorators.run_function
def run(ctx: context.RunContextProducer) -> list[dict[str, str]]:
    """Creates a list of work item payloads."""
    work_items = []

    # TODO: Use the following template code to create proper work items:
    payload = {
        "client_id": "",
        "client_name": "",
    }
    work_items.append(payload)
    
    if ctx.cfg.MAX_WORK_ITEMS:
        log.warn(f'MAX_WORK_ITEMS set - only creating {ctx.cfg.MAX_WORK_ITEMS} work items!')
        return work_items[:int(ctx.cfg.MAX_WORK_ITEMS)]
    
    return work_items
