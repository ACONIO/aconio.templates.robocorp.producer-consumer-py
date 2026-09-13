"""Robocorp Control Room API Wrapper - workspace interactions."""

import aconio.control_room._api as _api


class _WorkspacesAPIWrapper:
    """Wrapper for the Robocorp Control Room API 'workspaces' endpoints."""

    def __init__(self, api: _api._ControlRoomAPIWrapper) -> None:
        self.api = api

    def get_workspace(
        self,
        workspace_id: str,
    ):
        """
        Return all information of the current workspace.

        Args:
            workspace_id:
                The workspace id of the control room.

        Returns:
            workspace_info:
                Information of the given workspace.
        """
        return self.api.get(route=f"/workspaces/{workspace_id}")
