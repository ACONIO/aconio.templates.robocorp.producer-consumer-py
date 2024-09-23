"""Handle UI interactions with the BMD application."""

from robocorp import windows, log

from aconio.core import utils
from aconio.bmd import cli as ntcs_cli
from aconio.bmd._config import config, ExecutableType


class BMDError(Exception):
    """BMD related error."""


def bmd_window(**kwargs) -> windows.WindowElement:
    """Return the main BMD window."""
    return windows.find_window(config().ntcs_window_locator, **kwargs)


def close_tab() -> None:
    """Close an open BMD tab."""

    bmd_window().send_keys("{ESC}")


def open_application(
    ntcs_exec_type: ExecutableType | str | None = None,
    params: dict[str, str] | None = None,
) -> None:
    """Open the BMD application.

    Args:
        ntcs_exec_type:
            NTCS executable type. Can either be "NTCS" or "EXEC". If unset,
            the exec type of the module config (`config().ntcs_exec_type`)
            will be used.
        params:
            Extra startup parameters passed to the CLI command to start BMD.
            Defaults to `None`.
    """

    executable = ntcs_cli.BMDExecutable(
        config().ntcs_dir, ntcs_exec_type or config().ntcs_exec_type
    )

    log.info(f"Starting BMD executable at {executable.executable_path}")
    executable.start(params=params)

    try:
        # Starting the BMD window can take up to 50 seconds (default timeout
        # of bmd_window() is 10 seconds)
        utils.wait_until_succeeds(
            5,
            0,
            bmd_window,
        )
    except windows.ElementNotFound:
        log.warn("Failed to detect BMD window after booting executable...")

        # Check for bmd update notification
        if windows.desktop().find(
            "class:TBMDNCMultiProgressFRM", raise_error=False
        ):
            log.info("BMD update notification detected. Waiting for completion")
        else:
            # pylint: disable-next=raise-missing-from
            raise BMDError(
                "Failed to detect BMD window or update notification!"
            )

        # Wait a maximum of 500 seconds (timeout of bmd_window() + wait time
        # between function retries * 10) for BMD window to appear
        utils.wait_until_succeeds(
            10,
            40,
            bmd_window,
        )


def close_application() -> None:
    """Close the BMD application."""

    try:
        bmd_window().find('name:"Schließen" and control:ButtonControl').click()

        close_app_popup = windows.desktop().find(
            'name:"Achtung"', raise_error=False, timeout=4
        )

        if close_app_popup is not None:
            close_app_popup.find('name:"Beenden" and class:TButton').click()

    except windows.ElementNotFound:
        log.warn("Failed to close BMD app, trying to force kill it")
        bmd_window().close_window()
