"""Wrapper for the Robocorp Control Room API."""

import os

# Exposed by the module
import aconio.control_room.work_items as work_items
import aconio.control_room.process_run as process_run
import aconio.control_room.step_run as step_run
import aconio.control_room.workspace as workspace

from aconio.control_room._config import config


def is_cr_run() -> bool:
    return bool(os.environ.get("RC_ACTIVITY_ID"))
