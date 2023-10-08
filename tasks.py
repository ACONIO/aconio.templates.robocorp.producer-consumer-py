"""This file holds the high-level logic of the process and
performs mainly work item management and error-handling."""

from robocorp.tasks import task
from robocorp import workitems
from robocorp import log

from bot.common import setup, teardown
from bot.consumer import run as run_consumer
from bot.producer import run as run_producer


@task
def producer():
    """Create output work items for the consumer."""

    try:
        setup()
        wi_payloads = run_producer()

        for payload in wi_payloads:
            workitems.outputs.create(payload)
    except Exception as err:
        log.exception(str(err))
    finally:
        teardown()


@task
def consumer():
    """Process all the work items created by the producer."""

    try:
        setup()
        for item in workitems.inputs:
            try:
                run_consumer()
                item.done()

            # TODO: adapt exceptions below
            except AssertionError as err:
                item.fail("BUSINESS", code="INVALID_ORDER", message=str(err))
            except KeyError as err:
                item.fail("APPLICATION", code="MISSING_FIELD",
                          message=str(err))
    except Exception as err:
        log.exception(str(err))
    finally:
        teardown()
