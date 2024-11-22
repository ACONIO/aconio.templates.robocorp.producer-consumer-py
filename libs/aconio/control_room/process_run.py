"""Robocorp Control Room API - process run interactions."""

from ._api import api


def stop_process_run(
    workspace_id: str,
    process_run_id: str | None = None,
) -> None:
    """
    Stop a running process in the robocorp control room.

    Args:
        workspace_id:
            The workspace id of the control room.
        process_run_id:
            The id of the process run you want to stop.
    """

    body = {
        "set_remaining_work_items_as_done": False,
        "terminate_ongoing_activity_runs": True,
    }
    api().post(
        route=f"/workspaces/{workspace_id}/process-runs/{process_run_id}/stop",
        body=body,
    )
