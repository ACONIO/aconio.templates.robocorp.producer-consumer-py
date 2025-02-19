"""Interactions with the "Drittschuldner-Assistent" in Advokat."""

from robocorp import windows

from aconio.advokat import ui as advokat
from aconio.advokat.ui._locators import locators
from aconio.advokat.ui._desktop import desktop


def window(**kwargs) -> windows.WindowElement:
    """Return the Advokat "Drittschuldner-Assistent" window."""
    return advokat.erv.window().find_child_window(
        'name:"Drittschuldner-Assistent"', **kwargs
    )


def is_open() -> bool:
    """Return whether the "Drittschuldner-Assistent" window is open."""
    return window(raise_error=False) is not None


def confirm() -> None:
    """Save & close the current "Drittschuldner-Assistent" window."""
    window().send_keys("{LALT}O")


def cancel() -> None:
    """Cancel & close the current "Drittschuldner-Assistent" window."""
    desktop().click(locators().cancel_button)

    if is_open():
        raise ValueError("Failed to close 'Drittschuldner-Assistent' window.")


def open_first_deptor() -> None:
    """Open "Personenstamm" of first debtor in "DS-Assistent" window."""

    for _ in range(3):
        window().send_keys("{ENTER}")

    window().send_keys("{LCTRL}{ENTER}")


def enter_person_data() -> None:
    """Enter default "Drittschuldner" data in "Person - Stammdaten" window."""

    # Verify the "Person - Stammdaten" window is open
    person_window = _get_person_data_window()

    # Open the "Weitere" tab
    person_window.send_keys("{LALT}W")

    # Navigate to the "Anrede" field & select "Sehr geehrte Damen und Herren"
    person_window.send_keys("{LALT}N")
    person_window.send_keys("DH", send_enter=True)

    # Navigate to the "Beziehung" field & select "Drittschuldner"
    person_window.send_keys("{LALT}H")
    person_window.send_keys("DR", send_enter=True)

    # Save the changes
    person_window.send_keys("{LALT}O")

    # If person_window is still open, check for
    # "Geben Sie eine Kurzbezeichnung ein" dialog & handle it
    if person_window:
        _handle_kurzbezeichnung_dialog(person_window)


def _get_person_data_window() -> windows.WindowElement:
    """Return the "Person - Stammdaten" window."""
    person_window = window().find_child_window(
        'name:"Person - Stammdaten"', raise_error=False
    )

    if not person_window:
        raise ValueError("The 'Person - Stammdaten' window is not open.")

    return person_window


def _handle_kurzbezeichnung_dialog(
    person_window: windows.WindowElement,
) -> None:
    """Handle the "Geben Sie eine Kurzbezeichnung ein" dialog."""

    if dialog := person_window.find_child_window(
        'name:"ADVOKAT"', raise_error=False
    ):
        dialog.send_keys("{ENTER}")
