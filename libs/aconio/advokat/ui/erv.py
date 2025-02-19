"""Interface for the Advokat program "Elektronischer Rechtsverkehr"."""

import enum

from robocorp import windows


class ViewType(enum.StrEnum):
    OUTBOUND = enum.auto()
    """Equivalent to ERV "Hinverkehr"."""

    INBOUND = enum.auto()
    """Equivalent to ERV "Rückverkehr"."""


def window(**kwargs) -> windows.WindowElement:
    """Return the Advokat "Elektronischer Rechtsverkehr" window."""
    return windows.find_window('name:"Elektronischer Rechtsverkehr"', **kwargs)


def close() -> None:
    menu = window().find('name:"Anwendungsmenü"').find('name:"Programme"')
    menu.click()

    menu.find('control:MenuItemControl and subname:"Schließen"').click()


def select_view(erv_type: ViewType) -> None:
    """Switch between the ERV views "Hinverkehr" and "Rückverkehr"."""
    match erv_type:
        case ViewType.OUTBOUND:
            window().send_keys("{LALT}H")
        case ViewType.INBOUND:
            window().send_keys("{LALT}R")


def set_filter(
    date_from: str | None = None,
    date_to: str | None = None,
    doc_type: str | None = None,
    act: str | None = None,
) -> None:
    """Set a filter within the "Elektronischer Rechtsverkehr" window.

    Args:
        date_from:
            Value for the Advokat "Datum von" field.
        date_to:
            Value for the Advokat "bis" field.
        doc_type:
            Value for the Advokat "Schriftsatzart" field. Can be
            the abbreviation or the full name of the document type.
        act:
            Value for the Advokat "Akt" field.
    """

    # Open filter window & wait for loading
    window().send_keys("{CTRL}F")
    filter_window = window().find('name:"Filter ERV"')

    if date_from:
        filter_window.send_keys("{LALT}V")
        filter_window.send_keys(f"{date_from}", send_enter=True)

    if date_to:
        filter_window.send_keys("{LALT}B")
        filter_window.send_keys(f"{date_to}", send_enter=True)

    if doc_type:
        filter_window.send_keys("{LALT}A")
        filter_window.send_keys(f"{doc_type}", send_enter=True)

    if act:
        filter_window.send_keys("{LALT}K")
        filter_window.send_keys(f"{act}", send_enter=True)

    # Close filter window
    window().send_keys("{LALT}O")

    # Reload ERV window after filtering
    window().send_keys("{F8}")
