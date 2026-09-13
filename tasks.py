"""Task definitions and setup/teardown handling."""

import faulthandler

import robocorp.tasks
import robocorp.workitems

import aconio.botdata

import bot.consumer
import bot.producer
import bot.reporter

import bot._items as _items
import bot._config as _config

faulthandler.disable()


@robocorp.tasks.setup(scope="task")
def before_each(tsk):

    # TODO: Insert correct process name, or remove if not temporary directory
    # is required
    aconio.botdata.create("<process_name>")  # Temporary robot directory

    _config.load()
    _config.config().dump()

    match tsk.name:
        case "producer":
            bot.producer.setup()
        case "consumer":
            bot.consumer.setup()
        case "reporter":
            bot.reporter.setup()


@robocorp.tasks.teardown(scope="task")
def after_each(tsk):
    match tsk.name:
        case "producer":
            bot.producer.teardown()
        case "consumer":
            bot.consumer.teardown()
        case "reporter":
            bot.reporter.teardown()


@robocorp.tasks.task
def producer():
    """Create output work items for the consumer."""

    for item in bot.producer.run():
        _items.create_rc_wi_from_pydantic_model(item)


@robocorp.tasks.task
def consumer():
    """Process all the work items created by the producer."""

    for item in robocorp.workitems.inputs:
        with item:
            bot.consumer.run(_items.Item.model_validate(item.payload))


@robocorp.tasks.task
def reporter():
    """Report expected failures (BREs) to the employee."""

    bot.reporter.run(items=list(robocorp.workitems.inputs))
