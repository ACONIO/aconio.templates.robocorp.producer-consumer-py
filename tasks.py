"""Task definitions and setup/teardown handling."""

import faulthandler

import bot.consumer
import bot.producer
import bot.reporter

from robocorp import workitems, tasks

from aconio import botdata

from bot import _items, _config

faulthandler.disable()


@tasks.setup(scope="task")
def before_each(tsk):

    # TODO: Insert correct process name, or remove if not temporary directory
    # is required
    botdata.create("<process_name>")  # Temporary robot directory

    _config.load()
    _config.config().dump()

    match tsk.name:
        case "producer":
            bot.producer.setup()
        case "consumer":
            bot.consumer.setup()
        case "reporter":
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

    for item in bot.producer.run():
        _items.create_rc_wi_from_pydantic_model(item)


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
