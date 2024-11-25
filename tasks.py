"""Task definitions and setup/teardown handling."""

import os
import faulthandler

import bot.consumer
import bot.producer
import bot.reporter

from robocorp import log, workitems, tasks, vault

from aconio import botdata, guards

from bot import _items, _config


faulthandler.disable()


@tasks.setup(scope="task")
def before_each(tsk):

    # TODO: Insert correct process name, or remove if not temporary directory
    # is required
    botdata.create("<process_name>")  # Temporary robot directory

    # List of Jinja2 environments. Directories are searched in order, so the
    # first matching template overwrites any following ones.
    jinja_envs = []

    match _config.env():
        case "dev":
            _config.set_config_path(f"devdata/{_config.env()}.config.yaml")

        case "prod" | "test":
            azure_creds = vault.get_secret("azure_fileshare")

            botdata.load_process_config_from_azure(
                storage_dir_path=os.environ.get("AZURE_CONFIG_DIR"),
                account_url=azure_creds["account_url"],
                share_name=azure_creds["share_name"],
                access_key=azure_creds["access_key"],
            )

            _config.set_config_path(
                os.path.join(
                    botdata.config_dir(), f"{_config.env()}.config.yaml"
                )
            )
            jinja_envs.append(os.path.join(botdata.config_dir(), "templates"))

    # Default jinja templates, overwritten with Azure templates if present
    jinja_envs.append(os.path.join(os.environ.get("ROBOT_ROOT"), "templates"))

    _config.dump()

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

    for wi in bot.producer.run():
        log.console_message(
            f"Creating for item for client '{wi.client.bmd_number}...'\n",
            "stdout",
        )
        workitems.outputs.create(wi.model_dump())


@tasks.task
def consumer():
    """Process all the work items created by the producer."""

    max_fail = 3  # TODO Fetch from Config
    notification_mail = "dummy@aconio.net"  # TODO Fetch from config

    for item in workitems.inputs:
        with item:
            if _config.is_prod():
                with guards.MaxFailedGuard(max_fail, notification_mail):
                    bot.consumer.run(_items.Item.model_validate(item.payload))
            else:
                bot.consumer.run(_items.Item.model_validate(item.payload))


@tasks.task
def reporter():
    """Report expected failures (BREs) to the employee."""

    bot.reporter.run(items=list(workitems.inputs))
