"""Task definitions and setup/teardown handling."""

import faulthandler

import bot.consumer
import bot.producer
import bot.reporter

from robocorp import log, workitems, tasks

from aconio import botdata

from bot import _items, _config


faulthandler.disable()


@tasks.setup(scope="task")
def before_each(tsk):

    # TODO: Insert correct process name, or remove if not temporary directory
    # is required
    botdata.create("<process_name>")  # Temporary robot directory

    match tsk.name:
        case "producer":
            _config.dump(bot.producer.config())
            bot.producer.setup()
        case "consumer":
            _config.dump(bot.consumer.config())
            bot.consumer.setup()
        case "reporter":
            _config.dump(bot.reporter.config())
            bot.reporter.setup()


@tasks.teardown(scope="task")
def after_each(tsk):
    match tsk.name:
        case "producer":
            bot.producer.teardown()
        case "consumer":
            bot.consumer.teardown()
        case "reporter":
            bot.reporter.teardown()


@tasks.task
def producer():
    """Create output work items for the consumer."""

    for wi in bot.producer.run():
        log.console_message(
            f"Creating for item for client '{wi.client.bmd_number}...'\n",
            "stdout",
        )
        workitems.outputs.create(wi.model_dump())


@tasks.task
def consumer():
    """Process all the work items created by the producer."""

    for item in workitems.inputs:
        with item:
            bot.consumer.run(_items.Item.model_validate(item.payload))


@tasks.task
def reporter():
    """Report expected failures (BREs) to the employee."""

    bot.reporter.run(items=list(workitems.inputs))
