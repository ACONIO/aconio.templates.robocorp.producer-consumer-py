"""Handle UI interactions with the BMD application."""

from robocorp import windows, log

from aconio import utils
from aconio.bmd import cli, _errors
from aconio.bmd._config import config


def window(**kwargs) -> windows.WindowElement:
    """Return the main BMD window."""
    return windows.find_window(config().bmd_locator, **kwargs)


def close_tab() -> None:
    """Close an open BMD tab."""
    window().send_keys("{ESC}")


def open_application(
    timeout: float = 3,
    retries: int = 6,
    executable: cli.BMDExecutable | None = None,
    params: dict[str, str] | None = None,
    ui_login: bool = False,
) -> None:
    """Open the BMD application.

    Args:
        retries:
            Number of times trying to find the BMD window. One retry is
            equal to waiting 10 seconds for the BMD window to appear.
            Defaults to `6`.
        timout:
            Thr number of seconds to wait between searching the BMD window.
        executable:
            A custom NTCS executable. Per default, the BMD executable set via
            the module configuration will be started. Therefore, parameters
            such as the login details will be passed automatically. If a
            different BMD instance should be started, a custom BMD executable
            can be passed here. Defaults to `None`.
        params:
            Extra startup parameters passed to the CLI command to start BMD.
            Defaults to `None`.
        ui_login:
            If `True`, the login will be performed via the BMD login window
            instead of passing the credentials via CLI. This requires that
            BMD login parameters have been set in the module configuration.
            Defaults to `False`.

    Raises:
        ValueError:
            If `ui_login` is `True` but BMD login parameters have not been
            set in the module configuration.
    """

    if not executable:
        executable = cli.ntcs_cli()

    executable.start(params=params)

    if ui_login:
        _perform_ui_login()

    _wait_for_bmd_window(retries=retries, timeout=timeout)


def _perform_ui_login() -> None:
    """Login via the BMD login window."""

    if not config().login_params:
        raise ValueError(
            "Cannot login via BMD UI due to missing credentials! "
            "Please use `set_login_details()` in the module configuration."
        )

    login_window = windows.desktop().find(
        'name:"Datenbanklogin" and class:TBMDFRMLogin', timeout=50
    )

    login_window.send_keys("{LALT}D")
    login_window.send_keys(config().login_params.db)

    login_window.send_keys("{LALT}B")
    login_window.send_keys(config().login_params.username)

    login_window.send_keys("{LALT}P")
    login_window.send_keys(config().login_params.password)

    login_window.find('name:"Anmelden" and class:TBMDButton').click()


def _wait_for_bmd_window(
    retries: int = 6, timeout: float = 3, update_multiplier: int = 10
) -> None:
    """Wait for the BMD window to appear.

    Args:
        retries:
            Number of times trying to find the BMD window. One retry is
            equal to waiting 10 seconds for the BMD window to appear.
            Defaults to `6`.
        timout:
            Thr number of seconds to wait between searching the BMD window.
        update_multiplier:
            Multiplier for the number of retries in case a BMD update is
            detected. This is used to wait longer for the BMD window to
            appear due to an update. Defaults to `10`.

    Raises:
        BMDError:
            If the BMD window does not appear after after waiting for 60
            seconds (or 600 seconds in case a BMD update is performed).
    """

    try:
        utils.wait_until_succeeds(retries, 0, _find_bmd_window)
    except _errors.BMDUpdateDetectedError:
        log.warn("BMD update notification detected.")

        retries = retries * update_multiplier
        utils.wait_until_succeeds(
            retries, timeout, _find_bmd_window, detect_updates=False
        )

    except windows.ElementNotFound:
        # pylint: disable=raise-missing-from
        raise _errors.BMDError(
            "Failed to detect BMD window or update notification!"
        )


def _find_bmd_window(detect_updates: bool = True) -> None:
    """Raise if the BMD window is not found.

    Args:
        detect_updates:
            If `True`, an error is raised if the BMD update
            notification is detected. Defaults to `True`.

    Raises:
        BMDError:
            If the BMD window is not found.
        BMDUpdateDetectedError:
            If the BMD update notification is detected. Can be
            disabled using `detect_updates=False`.
    """

    # For detecting update loading screens or version info dialogs,
    # we purposefully set the timeout to 1 second to ensure that
    # these checks do not cost too much time.

    if detect_updates:
        if _detect_bmd_update(timeout=1):
            raise _errors.BMDUpdateDetectedError(
                "BMD update notification detected."
            )

    _handle_version_info_dialog(timeout=1)
    window()


def _detect_bmd_update(timeout: int = 10) -> windows.WindowElement | None:
    """Find the BMD update notification window."""
    return windows.desktop().find(
        "class:TBMDNCMultiProgressFRM", raise_error=False, timeout=timeout
    )


def _handle_version_info_dialog(timeout: int = 10) -> None:
    """Catch the BMD version dialog and close it if it appears."""
    version_dialog = windows.desktop().find(
        'subname:"Neue Version gefunden"', raise_error=False, timeout=timeout
    )

    if version_dialog:
        version_dialog.click('subname:"Abbrechen"')


def close_application() -> None:
    """Close the BMD application."""

    try:
        window().find('name:"Schließen" and control:ButtonControl').click()

        close_app_popup = windows.desktop().find(
            'name:"Achtung"', raise_error=False, timeout=4
        )

        if close_app_popup is not None:
            close_app_popup.find('name:"Beenden" and class:TButton').click()

    except windows.ElementNotFound:
        log.warn("Failed to close BMD app, trying to force kill it")
        window().close_window()
