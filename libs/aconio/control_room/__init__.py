"""Wrapper for the Robocorp Control Room API."""

import os

# Exposed by the module
from aconio.control_room._config import config

from aconio.control_room.work_items import *
from aconio.control_room.process_run import *
from aconio.control_room.step_run import *
from aconio.control_room.workspace import *


def is_cr_run() -> bool:
    return bool(os.environ.get("RC_ACTIVITY_ID"))
