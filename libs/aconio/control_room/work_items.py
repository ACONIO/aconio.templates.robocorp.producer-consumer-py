"""Robocorp Control Room API Wrapper - work item interactions."""

import aconio.control_room._api as _api


class _WorkItemsAPIWrapper:
    """Wrapper for the Robocorp Control Room API 'work-items' endpoints."""

    def __init__(self, api: _api._ControlRoomAPIWrapper) -> None:
        self.api = api

    def list_work_items(
        self,
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

        work_items = self.api.get(
            route=f"/workspaces/{workspace_id}/work-items",
            params=params,
        )

        if step_id:
            work_items = [
                w for w in work_items if w.get("step").get("id") == step_id
            ]

        return work_items

    def get_work_item(
        self,
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

        work_item = self.api.get(
            route=f"/workspaces/{workspace_id}/work-items/{work_item_id}",
        )

        return work_item

    def batch_operation(
        self,
        workspace_id: str,
        operation: str,
        work_item_ids: list[str],
    ) -> None:
        """Return a work item.

        Args:
            workspace_id:
                The workspace id of the control room.
            operation:
                The operation to perform on the work items. Must be one of:
                "retry", "delete", "mark_as_done".
            work_item_ids:
                A list of work item ids to perform the operation on.
        """

        if operation not in ["retry", "delete", "mark_as_done"]:
            raise ValueError(
                f"Invalid work item batch operation: {operation}. "
                "Must be one of: retry, delete, mark_as_done."
            )

        body = {
            "batch_operation": operation,
            "work_item_ids": work_item_ids,
        }

        self.api.post(
            route=f"/workspaces/{workspace_id}/work-items/batch", body=body
        )
