"""Guard mechanism to prevent processes from consecutive failures."""

import os

import robocorp.tasks

import aconio.outlook as outlook
import aconio.control_room as cr


class FailGuard:
    """Prevent processes from consecutive failures."""

    def __init__(
        self,
        cr_api_key: str,
        max_fail_cnt: int,
        mail_recipients: str | list[str] | None = None,
    ) -> None:
        """Initialize the fail guard.

        Args:
            cr_api_key:
                Robocorp Control Room API key. Requires 'read_processes'
                and 'trigger_processes' permissions.
            max_fail_cnt:
                The maximum number of consecutive failed step-runs. When
                reached, the process is stopped by the guard.
            mail_recipients:
                The email address(es) to notify.
        """
        self.max_fail_cnt = max_fail_cnt
        self.mail_recipients = mail_recipients

        if not self.max_fail_cnt > 1:
            raise ValueError(
                f"max_fail_cnt must be > 1, got {self.max_fail_cnt}"
            )

        self.cr_api = self._init_control_room_connection(api_key=cr_api_key)

        self.workspace_id = os.environ.get("RC_WORKSPACE_ID")
        self.process_run_id = os.environ.get("RC_PROCESS_RUN_ID")

    def stop_process_if_max_failures_reached(
        self, task: robocorp.tasks.ITask
    ) -> None:
        """Stop process run if max number of consecutive failures is reached.

        Args:
            task:
                The currently executed Robocorp task. Can be obtained by
                calling `robocorp.tasks.get_current_task()`.
        """

        # Ignore non-control-room runs
        if not self.workspace_id or not self.process_run_id:
            return

        # Step runs are returned newest to oldest
        step_runs = self.cr_api.step_run.list_step_runs(
            workspace_id=self.workspace_id,
            process_run_id=self.process_run_id,
        )

        # Exit early if the current step-run is not considered failed
        if not self._is_current_step_run_considered_failed(task, step_runs[0]):
            return

        if self._max_counter_reached(step_runs):
            self._stop_process_run()

            if self.mail_recipients:
                self._send_notification_mail()

    def _init_control_room_connection(self, api_key: str) -> cr.ControlRoom:
        cr_api = cr.ControlRoom(
            config=cr.ControlRoomConfig(
                api_key=api_key,
            )
        )
        return cr_api

    def _max_counter_reached(self, step_runs: list[dict]) -> bool:
        # We start with 1 since the current step run is considered
        # failed at this point.
        consecutive_failures = 1

        # We drop the first step-run since it is the current one,
        # which we already know is considered failed.
        for run in step_runs[1:]:
            if self._is_considered_failed_step_run(run):
                consecutive_failures += 1
                if consecutive_failures >= self.max_fail_cnt:
                    return True
            else:
                return False

        return False

    def _is_current_step_run_considered_failed(
        self, task: robocorp.tasks.ITask, step_run: dict
    ) -> bool:
        """Determine if the current step-run is considered failed.

        To determine if the *current* step-run is considered failed, we
        also need to check the status of the current Robocorp task.

        This is because the current step-run fetched from the Robocorp
        API is in state "in_progress". Hence, if we were to use
        "_is_considered_failed_step_run", it would not exit early due to
        a "completed" (still "in_progress") state, and it would therefore
        check the number of successful work items. If the current run had
        only 1 item left processing and it was successful, it would be
        considered as a failed step-run, (items < 2).
        """
        if task.status not in (
            robocorp.tasks.Status.FAIL,
            robocorp.tasks.Status.NOT_RUN,  # Indicates setup() failure
        ):
            return False

        return self._is_considered_failed_step_run(step_run)

    def _is_considered_failed_step_run(self, step_run: dict) -> bool:
        """Determine if a step-run is considered failed.

        We still consider a step-run to be successful if it has processed
        => 2 work items successfully and failed afterwards. This should reset
        the counter of consecutive failures, because the fail guard should only
        trigger if the process is failing continually due to an environment-
        related issue (e.g. Outlook pop-up on every work item).

        Why not consider a step-run with 1 successful work items as successful?

        In some cases, an environment-related problem might cause every second
        work item to fail (e.g. pop-up at the end of processing each work item,
        failing the second work item). In this case, the process would always
        have a single processed work item, but it would still be failing
        continually.
        """

        # "Completed" means "successful" in Robocorp terms
        if step_run.get("state") == "completed":
            return False

        step_run_items = self.cr_api.work_items.list_work_items(
            workspace_id=self.workspace_id,
            process_run_id=self.process_run_id,
            step_id=step_run.get("id"),
        )

        successful_items = [
            item for item in step_run_items if item.get("state") == "done"
        ]

        return len(successful_items) < 2

    def _stop_process_run(self) -> None:
        self.cr_api.process_run.stop_process_run(
            self.workspace_id,
            self.process_run_id,
            "Stopped by Fail Guard.",
        )

    def _send_notification_mail(self) -> None:
        workspace_info = self.cr_api.workspaces.get_workspace(self.workspace_id)

        org_name = workspace_info.get("organization").get("name")

        subject = (
            f"[{org_name}: {self.process_run_id}] Process Run Stopped "
            "by Fail Guard."
        )

        outlook.start()
        outlook.send_email(
            subject=subject,
            body="Process run stopped due to consecutive failures!",
            html_body=True,
            to=self.mail_recipients,
        )
