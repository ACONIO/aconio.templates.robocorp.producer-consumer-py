"""Handle UI interactions with the Advokat application."""

import _ctypes
import subprocess
import faulthandler

import robocorp.log as log
import robocorp.windows as windows

# Expose the submodules for easier access
import aconio.advokat.ui.erv as erv
import aconio.advokat.ui.act_mgmt as act_mgmt
import aconio.advokat.ui.ds_assistant as ds_assistant

faulthandler.disable()


def window(**kwargs) -> windows.WindowElement:
    """Return the main Advokat window."""
    return windows.find_window(r'regex:"ADVOKAT - .*"', **kwargs)


def is_open(timeout: int = 10) -> bool:
    """Return whether the Advokat window is open."""
    try:
        advokat_window = window(raise_error=False, timeout=timeout)
        return advokat_window is not None
    except _ctypes.COMError as e:
        log.warn("Failed to check if Advokat is open: ", e)
        return False


def open_application(
    exe_path: str, installation_name: str | None = None
) -> None:
    """Open the Advokat application.

    Args:
        exe_path:
            Path to the Advokat executable.
        installation_name:
            Name of the Advokat installation to open.
    """
    subprocess.run([exe_path], check=True)

    if installation_name:
        _choose_advokat_installation(installation_name)

    _handle_update_dialog()

    _wait_for_advokat_window(retries=5)


def _choose_advokat_installation(name: str) -> None:
    select_dialog = windows.find_window('name:"ADVOKAT - Installationen"')
    select_dialog.click(f'name:"{name}" and control:"ListItemControl"')
    select_dialog.click('name:"OK" and control:"ButtonControl"')


def _handle_update_dialog() -> None:
    """Handle the Advokat update dialog if it appears."""

    dialog = windows.find_window(
        'subname:"ADVOKAT"', timeout=4, raise_error=False
    )

    if not dialog:
        return

    # The dialog can only be properly identified as an update dialog
    # if it contains a "Fortsetzen" button.
    continue_button = dialog.find(
        'subname:"Fortsetzen" and control:"ButtonControl"',
        timeout=2,
        raise_error=False,
    )

    if continue_button:
        continue_button.click()


def _wait_for_advokat_window(retries: int, timeout: int = 10) -> None:
    for _ in range(retries):
        if is_open(timeout):
            return

    raise RuntimeError("Failed to open Advokat application.")


def close_application() -> None:
    """Close the Advokat application."""

    try:
        _close_advokat_window()
    except Exception as exc:  # pylint: disable=broad-except
        log.debug(f"Failed to close Advokat window: {exc}")

    if is_open(timeout=2):
        subprocess.run(["taskkill", "/f", "/im", "Advokat3.exe"], check=True)


def _close_advokat_window() -> None:
    """Close the Advokat window."""
    menu = window().find('name:"Anwendungsmenü"').find('name:"Programme"')
    menu.click()

    menu.find('control:MenuItemControl and subname:"Beenden"').click(
        wait_time=1
    )


def start_program(name: str) -> None:
    """Start one of the Advokat programs from the main menu.

    Args:
        name:
            Name of the program, e.g. "ERV". The name must be equivalent to
            an item from the Advokat "Programme" menu bar.
    """

    menu = window().find('name:"Anwendungsmenü"').find('name:"Programme"')
    menu.click()

    menu.find(f'control:MenuItemControl and name:"{name}"').click()
