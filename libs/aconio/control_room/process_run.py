"""Robocorp Control Room API Wrapper - process run interactions."""

import aconio.control_room._api as _api


class _ProcessRunAPIWrapper:
    """Wrapper for the Robocorp Control Room API 'process-runs' endpoints."""

    def __init__(self, api: _api._ControlRoomAPIWrapper) -> None:
        self.api = api

    def stop_process_run(
        self,
        workspace_id: str,
        process_run_id: str,
        reason: str,
        terminate: bool = False,
    ) -> None:
        """
        Stop a running process in the robocorp control room.

        Args:
            workspace_id:
                The workspace id of the control room.
            process_run_id:
                The id of the process run you want to stop.
            reason:
                The reason for stopping the process run.
            terminate:
                Whether to terminate the ongoing activity runs.
        """

        body = {
            "set_remaining_work_items_as_done": False,
            "terminate_ongoing_activity_runs": terminate,
            "reason?": reason,
        }

        self.api.post(
            route=(
                f"/workspaces/{workspace_id}/process-runs/{process_run_id}/stop"
            ),
            body=body,
        )
