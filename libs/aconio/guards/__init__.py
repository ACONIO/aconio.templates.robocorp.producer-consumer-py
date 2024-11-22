"""A set of context managers."""

import os
import contextlib

import aconio.control_room as cr
import aconio.outlook as outlook


# pylint: disable=invalid-name
@contextlib.contextmanager
def MaxFailedGuard(
    max_fail: int,
    notification_mail: str | None = None,
    workspace_id=os.environ.get("RC_WORKSPACE_ID"),
    process_run_id=os.environ.get("RC_PROCESS_RUN_ID"),
):
    """Stop process if `max_fail` step-runs fail in a row.
    Args:
        max_fail:
            The maximum number of failed step-runs in a row.
        notification_mail:
            The email address to send the notification mail to.
        workspace_id:
            The workspace id of the process.
        process_run_id:
            The process run id of the process.
    """
    try:
        yield
    except Exception:  # pylint: disable=broad-except
        step_runs = cr.list_step_runs(workspace_id, process_run_id)

        if _is_stop_process(step_runs, max_fail - 1):
            cr.stop_process_run(workspace_id, process_run_id)

            if notification_mail:
                _send_notification_mail(
                    notification_mail, workspace_id, process_run_id
                )


def _is_stop_process(step_runs: list[dict], max_fail: int) -> bool:
    """Return `True` if multiple step runs have failed in a row.
    Args:
        step_runs:
            A list of step_runs from the current running process.
        max_fail:
            The maximum number of failed step-runs in a row.
    """
    consecutive_failures = 0

    for run in step_runs:
        if run.get("state") == "failed":
            consecutive_failures += 1
            if consecutive_failures >= max_fail:
                return True
        else:
            consecutive_failures = 0

    return False


def _send_notification_mail(
    notification_mail: str, workspace_id: str, process_run_id: str
) -> None:
    """Send a notification mail to the specified email address.
    Args:
        notification_mail:
            The email address to send the notification mail to.
    """
    workspace_info = cr.get_workspace(workspace_id)

    org_name = workspace_info.get("organization").get("name")
    body = "Process run terminated due to multiple failed step-runs in a row!"

    outlook.start()
    outlook.send_email(
        subject=f"[{org_name}: {process_run_id}] Process Run Terminated.",
        body=body,
        html_body=True,
        to=notification_mail,
    )
