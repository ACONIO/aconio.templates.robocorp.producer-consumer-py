"""Handle UI interactions with the BMD application."""

from robocorp import windows, log

from aconio.utils import utils
from aconio.bmd import cli, _errors
from aconio.bmd._config import config


def window(**kwargs) -> windows.WindowElement:
    """Return the main BMD window."""
    return windows.find_window(config().bmd_locator, **kwargs)


def close_tab() -> None:
    """Close an open BMD tab."""
    window().send_keys("{ESC}")


def open_application(
    executable: cli.BMDExecutable | None = None,
    params: dict[str, str] | None = None,
    ui_login: bool = False,
) -> None:
    """Open the BMD application.

    Args:
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

    _wait_for_bmd_window()


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


def _wait_for_bmd_window() -> None:
    """Wait for the BMD window to appear.

    Raises:
        BMDError:
            If the BMD window does not appear after after waiting for 50
            seconds, or 500 seconds in case a BMD update is performed.
    """

    # Max time to wait for the BMD window to appear.
    timeout = 60

    if _find_update_notification():
        log.warn("BMD update notification detected.")
        timeout = 600

    # Provided that the default timeout of robocorp.windows is 10
    # seconds, we can calculate the number of retries needed.
    retries = timeout // 10

    try:
        utils.wait_until_succeeds(retries, 0, _find_bmd_window)
    except windows.ElementNotFound:
        # pylint: disable-next=raise-missing-from
        raise _errors.BMDError(
            "Failed to detect BMD window or update notification!"
        )


def _find_update_notification() -> windows.WindowElement | None:
    """Find the BMD update notification window."""
    # Here we keep the default timeout of 10 seconds to ensure enough
    # time passes for the update notification to appear.
    return windows.desktop().find(
        "class:TBMDNCMultiProgressFRM", raise_error=False
    )


def _find_bmd_window() -> None:
    """Raise if the BMD window is not found."""
    # Here, we purposefully set the timeout to 0 seconds to ensure that the
    # check for a version dialog does not cost too much time.
    _catch_version_dialog(timeout=0)
    window()


def _catch_version_dialog(timeout: int = 10) -> None:
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
