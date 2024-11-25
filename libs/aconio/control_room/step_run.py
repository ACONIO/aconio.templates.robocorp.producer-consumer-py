"""Robocorp Control Room API - step run interactions."""

from ._api import api


def list_step_runs(
    workspace_id: str,
    process_run_id: str | None = None,
) -> list[dict]:
    """
    Get a list of all current step runs from a running process.

    Args:
        workspace_id:
            The workspace id of the control room.
        process_run_id:
            The id of the process run you want to stop.

    Returns:
        step_runs:
            A list of step runs.
    """
    params = {}

    if process_run_id:
        params["process_run_id"] = process_run_id

    step_runs = api().get(
        route=f"/workspaces/{workspace_id}/step-runs",
        params=params,
    )

    return step_runs
