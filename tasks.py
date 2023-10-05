"""This file holds the high-level logic of the process and
performs mainly work item management and error-handling."""

from robocorp.tasks import task
from robocorp import workitems

from bot.common import setup, teardown
from bot import consumer
from bot import producer


@task
def producer():
    """Create output work items for the consumer."""
    setup()

    try:
        wi_payloads = producer.run()

        for payload in wi_payloads:
            workitems.outputs.create(payload)
    finally:
        teardown()


@task
def consumer():
    """Process all the work items created by the producer."""
    setup()

    try:
        for item in workitems.inputs:
            try:
                consumer.run()
                item.done()

            # TODO: adapt exceptions below
            except AssertionError as err:
                item.fail("BUSINESS", code="INVALID_ORDER", message=str(err))
            except KeyError as err:
                item.fail("APPLICATION", code="MISSING_FIELD",
                          message=str(err))

    finally:
        teardown()
