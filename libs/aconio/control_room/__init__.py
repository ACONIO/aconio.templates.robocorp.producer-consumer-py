"""Interactions with the Robocorp Control Room API."""

import os

import aconio.control_room.step_run as step_run
import aconio.control_room.work_items as work_items
import aconio.control_room.workspaces as workspaces
import aconio.control_room.process_run as process_run

from aconio.control_room._api import _ControlRoomAPIWrapper
from aconio.control_room.config import ControlRoomConfig


def is_cr_run() -> bool:
    return bool(os.environ.get("RC_ACTIVITY_ID"))


class ControlRoom:

    def __init__(self, config: ControlRoomConfig) -> None:
        self.config = config
        self._api = _ControlRoomAPIWrapper(self.config)

        self.step_run = step_run._StepRunAPIWrapper(self._api)
        self.work_items = work_items._WorkItemsAPIWrapper(self._api)
        self.workspaces = workspaces._WorkspacesAPIWrapper(self._api)
        self.process_run = process_run._ProcessRunAPIWrapper(self._api)
