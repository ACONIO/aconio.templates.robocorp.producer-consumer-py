"""This file contains functions utilized by the producer."""

from typing import List

from robocorp import log

from .internal.tools import run_function


@run_function
def run() -> List[dict[str, str]]:
    """Creates a list of work item payloads."""
    output_work_items = []

    # TODO: Use the following template code to create proper work items:
    payload = {
        "client_id": "",
        "client_name": "",
    }
    output_work_items.append(payload)

    return output_work_items
