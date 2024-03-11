"""This file holds the high-level logic of the process and
performs mainly work item management and error-handling."""

import faulthandler

import bot.consumer
import bot.producer
import bot.reporter

from robocorp import log, workitems, tasks

from bot.core import contexts, utils


faulthandler.disable()


@tasks.task
def producer():
    """ Create output work items for the consumer. """

    ctx = contexts.RunContextProducer(
        # TODO: ADD CONFIGURATION.
    )
    with ctx:
        for wi in bot.producer.run(ctx):
            log.console_message(
                f"Creating for item for client '{wi.client_id}...'\n",
                "stdout",
            )
            workitems.outputs.create(wi.to_dict())


@tasks.task
def consumer():
    """ Process all the work items created by the producer. """

    ctx = contexts.RunContextConsumer(
        # TODO: ADD CONFIGURATION.
    )

    with ctx:
        for item in workitems.inputs:
            with item:
                utils.cleanup_folder(path=ctx.cfg.TEMP_DIR)

                bot.consumer.run(ctx, item)

                if ctx.cfg.TRACK_ITEMS_ASSET_NAME:
                    pass
                    # TODO: UNCOMMENT ON DEMAND.
                    # log.console_message(
                    #     "Increasing processed items counter asset "
                    #     f"'{ctx.cfg.TRACK_ITEMS_ASSET_NAME}' by 1\n",
                    #     "stdout"
                    # )
                    # ctx.item_counter.increment()


@tasks.task
def reporter():
    """ Reports expected failures (BREs) from the consumer to the employee. """

    ctx = contexts.RunContextReporter(start_outlook=True)
    with ctx:
        bot.reporter.run(ctx=ctx, inputs=list(workitems.inputs))
