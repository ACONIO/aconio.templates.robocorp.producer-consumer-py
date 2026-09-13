"""Reporter core logic."""

import time
import jinja2 as j2
import datetime
import functools

import robocorp.workitems

import aconio.outlook
import aconio.decorators

import bot._config as _config


@functools.lru_cache
def jinja() -> j2.Environment:
    return j2.Environment()


def setup() -> None:
    """Setup reporter process."""

    aconio.outlook.start(minimize=True)

    jinja().loader = j2.FileSystemLoader("templates")
    jinja().undefined = j2.StrictUndefined


def teardown() -> None:

    # This time.sleep() is necessary because of a bug where outlook
    # gets closed before an email can be sent. This timeout should give
    # Outlook enough time to send the last email properly.
    time.sleep(5)
    pass


@aconio.decorators.run_function
def run(items: list[robocorp.workitems.Input]):
    """Send a process report for failed work items."""

    content = generate_report(
        items=items,
        contact=_config.config().report.contact,
    )

    # TODO: Insert correct e-mail subject
    today = datetime.datetime.today().strftime("%d.%m.%Y")
    aconio.outlook.send_email(
        to=_config.config().report.recipients,
        subject=f"Process Report {today}",
        body=content,
        html_body=True,
        draft=_config.config().actions.send_email is False,
    )


def generate_report(
    items: list[robocorp.workitems.Input],
    contact: str,
) -> str:
    """Create a process report.

    Create a report for the employee informing them about failed work items
    and what steps need to be done to resolve the issues.

    Args:
        items:
            List of reporter work items.
        contact:
            Contact person at Aconio for further support.

    Returns:
        str:
            Formatted process report.
    """

    # Determine which error code of the `BusinessError` will result in which
    # message in the reporter e-mail.
    # pylint: disable=line-too-long
    codes = {
        "ERROR_MSG": "Fehlermeldung.",  # TODO: Add required error codes
    }

    infos = {
        i.payload["failed_wi_payload"]["client"]["bmd_number"]: codes[
            i.payload["failed_wi_code"]
        ]
        for i in items
    }

    return (
        jinja()
        .get_template("report.j2")
        .render(
            infos=infos,
            contact=contact,
        )
    )
