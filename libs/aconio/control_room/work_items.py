"""Robocorp Control Room API - work item interactions."""

from ._api import api


def list_work_items(
    workspace_id: str,
    process_id: str | None = None,
    process_run_id: str | None = None,
    step_id: str | None = None,
) -> list[dict]:
    """
    Return a list of work items.

    Args:
        workspace_id:
            The workspace id of the control room.
        process_id:
            The id of the process.
        process_run_id:
            The id of the process run you want to stop.
        step_id:
            The id of the current step.

    Returns:
        work_items:
            A list of work items.
    """
    params = {}

    if process_id:
        params["process_id"] = process_id

    if process_run_id:
        params["process_run_id"] = process_run_id

    work_items = api().get(
        route=f"/workspaces/{workspace_id}/work-items",
        params=params,
    )

    if step_id:
        work_items = [
            w for w in work_items if w.get("step").get("id") == step_id
        ]

    return work_items


def get_work_item(
    workspace_id: str,
    work_item_id: str,
) -> dict:
    """Return a work item.

    Args:
        workspace_id:
            The workspace id of the control room.
        work_item_id:
            The id of the work item.
    """

    work_item = api().get(
        route=f"/workspaces/{workspace_id}/work-items/{work_item_id}",
    )

    return work_item
