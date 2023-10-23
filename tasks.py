"""This file holds the high-level logic of the process and
performs mainly work item management and error-handling."""

from robocorp.tasks import task
from robocorp import workitems
from robocorp import log

from bot.context import RunContext, RobotType
from bot.common import cleanup_robot_tmp_folder
from bot.consumer import run as run_consumer
from bot.producer import run as run_producer


@task
def producer():
    """Create output work items for the consumer."""

    ctx = RunContext(RobotType.PRODUCER)  # Change the constructor arguments as wished.

    with ctx:
        cleanup_robot_tmp_folder(ctx.cfg.TEMP_DIR)

        wi_payloads = run_producer(ctx)

        for payload in wi_payloads:
            workitems.outputs.create(payload)


@task
def consumer():
    """Process all the work items created by the producer."""

    ctx = RunContext(RobotType.CONSUMER)  # Change the constructor arguments as wished.

    with ctx:
        for item in workitems.inputs:
            with item:
                cleanup_robot_tmp_folder(ctx.cfg.TEMP_DIR)

                run_consumer(ctx, item)

                item.done()
