"""Functions utilized by the reporter process."""

import functools

import jinja2 as j2

from datetime import datetime

from aconio import outlook
from aconio.core import decorators

from robocorp import workitems

from bot import _config


@functools.lru_cache
def config() -> _config.ReporterConfig:
    return _config.ReporterConfig()


@functools.lru_cache
def jinja() -> j2.Environment:
    return j2.Environment()


def setup() -> None:
    """Setup reporter process."""

    outlook.start(minimize=True)

    jinja().loader = j2.FileSystemLoader("templates")
    jinja().undefined = j2.StrictUndefined


def teardown() -> None:
    pass


@decorators.run_function
def run(items: list[workitems.Input]):
    """Send a process report for failed work items."""

    content = generate_report(
        items=items,
        contact=config().contact,
    )

    # TODO: Insert correct e-mail subject
    outlook.send_email(
        to=config().recipients,
        subject=f"Process Report {datetime.today().strftime('%d.%m.%Y')}",
        body=content,
        html_body=True,
        draft=config().test_mode,
    )


def generate_report(
    items: list[workitems.Input],
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
