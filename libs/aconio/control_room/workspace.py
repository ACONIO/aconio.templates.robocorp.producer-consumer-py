"""Robocorp Control Room API - workspace interactions."""

from ._api import api


def get_workspace(
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
    return api().get(route=f"/workspaces/{workspace_id}")
