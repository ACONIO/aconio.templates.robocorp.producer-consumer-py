"""Handle UI interactions with the DOMIZIL application."""

import functools
import subprocess
import time

from robocorp import windows, log

from RPA.Desktop import Desktop

from aconio.domizil import _errors
from aconio.domizil.ui._locators import locators
from aconio.core import utils


@functools.lru_cache
def _desktop() -> Desktop:
    return Desktop()


def window(**kwargs) -> windows.WindowElement:
    """Return the main DOMIZIL window."""
    return windows.find_window(
        'subname:"domizil+" and class:"TfrmMain"', **kwargs
    )


def close_tab() -> None:
    """Close an open DOMIZIL tab."""
    window().send_keys("{ESC}")


def open_application():
    """Open the DOMIZIL application."""
    # pylint: disable=line-too-long
    subprocess.run(
        r"\\EBSGDOMIZIL\DomizilPlusOMClient\bin\NetzwerkStarter.exe -OVERRIDEIMPORT -PROFIL:DomizilPlusOM",
        check=True,
    )
    _wait_for_domizil_window()


def _wait_for_domizil_window():
    """Wait for the DOMIZIL window to appear.

    Raises:
        DOMIZILError:
            If the DOMIZIL window does not appear after after waiting for 60
            seconds.
    """
    # Max time to wait for the DOMIZIL window to appear.
    timeout = 60

    # Provided that the default timeout of robocorp.windows is 10
    # seconds, we can calculate the number of retries needed.
    retries = timeout // 10

    try:
        utils.wait_until_succeeds(retries, 0, window)
    except windows.ElementNotFound:
        # pylint: disable-next=raise-missing-from
        raise _errors.DOMIZILError("Failed to detect DOMIZIL window!")


def close_application() -> None:
    """Close the DOMIZIL application."""
    try:
        close_tab()

        close_app_popup = windows.desktop().find(
            'name:"Bestätigung"', raise_error=False, timeout=4
        )

        if close_app_popup is not None:
            close_app_popup.find('name:"Ja" and class:TnetButton').click()
    except windows.ElementNotFound:
        log.warn("Failed to close DOMIZIL app, trying to force kill it")
        window().close_window()


def navbar_search(key_input: str):
    """
    Navigate to the main menu and enter an input.

    Args:
        key_input:
            The keystrokes that should be inputted into the main menu.
    """

    window().find('name:"Hauptmenü"').find(
        'control:"EditControl" and class:"TnetEdit"'
    ).send_keys(keys=key_input, wait_time=2).send_keys(keys="{F3}{Enter}")


def list_search(search_string: str) -> None:
    """Search in the current open DOMIZIL list."""

    window().send_keys("{F6}", wait_time=1)
    window().send_keys(search_string)

    prospect_window = window().find_child_window('name:"Arbeitsbereich"')
    prospect_window.find('name:"Suchen" and class:"TnetButton"').click(
        wait_time=2
    )


def open_documents_context_menu() -> None:
    window().send_keys("{Ctrl}o")


def save_templates(templates: list[str], output_dir: str):
    """Saves templates into the given directory."""

    save_template_window = window().find_child_window(
        'subname:"Vorlagenauswahl"'
    )

    for template in templates:
        save_template_window.find('class:"TnetEdit"').send_keys(template)
        save_template_window.find(
            'name:"Suchen" and class:"TnetButton"'
        ).click()

        _desktop().press_keys("down")
        _desktop().press_keys("enter")
        time.sleep(2)
        _desktop().click(locators().local_save)

        save_window = window().find_child_window(
            'subname:"Lokal Speichern - Datensatz Auswahl" and class:"TfrmRTFSelectRecord"'  # pylint: disable=line-too-long
        )

        save_window.find('class:"TnetDirEdit"').send_keys(output_dir)

        _desktop().click(locators().green_check_save_button)

        close_tab()

    close_tab()


def pre_definded_doc_search(postition: int) -> None:
    """Open a predefined document search.

    Args:
        postition:
            The position of predefined document search in the DOMIZIL
            "Dokumente > Suchen" context menu.
    """

    window().send_keys("{Ctrl}o")
    window().send_keys("{Down}{Down}")
    window().send_keys("{Enter}")

    # Depending on the position of the predefined search in the context menu,
    # we need to send the correct number of down key presses.
    window().send_keys("{Down}" * (postition - 1))
    window().send_keys("{Enter}", wait_time=2)


def export_pre_defined_search_documents(output_dir: str, timeout: int = 10):
    """Export the documents of the currently open predefined doc search.

    Args:
        output_dir:
            The directory to save the exported documents.
        timeout:
            The time to wait for the export to finish.
    """
    _desktop().press_keys("ctrl", "a")
    _desktop().click(locators().export_dialog)

    export_dialog = window().find_child_window(
        'name:"Export" and class:"TfrmDMSExport"'
    )
    export_dialog.find('class:"TnetDirEdit"').send_keys(output_dir)
    export_dialog.find('name:"Exportieren" and class:"TnetButton"').click()

    time.sleep(timeout)

    export_progess = export_dialog.find_child_window(
        'subname:"Fortschritt" and class:"TfrmDMSProgress"'
    )

    export_progess.send_keys("{Esc}")
    export_dialog.send_keys("{Esc}")
    close_confirmation_dialog(export_dialog)

    for _ in range(3):
        close_tab()


def close_confirmation_dialog(parent_window: windows.WindowElement):
    """Close the confirmation dialog."""

    confirmation_dialog = parent_window.find_child_window(
        'name:"Bestätigung" and class:"TfrmMessageDialog"'
    )

    confirmation_dialog.find('name:"Nein" and class:"TnetButton"').click()
