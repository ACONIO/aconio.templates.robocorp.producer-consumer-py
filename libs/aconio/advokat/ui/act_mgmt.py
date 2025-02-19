"""Interface for the Advokat program "Aktenverwaltung"."""

from robocorp import windows

from aconio.advokat.ui import _errors


def window(**kwargs) -> windows.WindowElement:
    """Return the Advokat "Aktenverwaltung" window."""
    return windows.find_window(
        r'regex:"ADVOKAT - \[Aktenverwaltung - .*\]"', **kwargs
    )


def close() -> None:
    menu = window().find('name:"Anwendungsmenü"').find('name:"Programme"')
    menu.click()

    menu.find('control:MenuItemControl and subname:"Schließen"').click()


def set_filter(
    predefined: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> None:
    """Set a filter within the "Aktenverwaltung" window.

    Args:
        predefined:
            Name of a predefined Advokat filter. Note that the filter must
            exist on the system for this argument to work. If set, the
            predefined filter will be applied first, then any other parameters
            will be set.
        date_from:
            Value for the Advokat "Datum von" field.
        date_to:
            Value for the Advokat "bis" field.
    """

    # Open filter window & wait for loading
    window().send_keys("{CTRL}F")
    filter_window = window().find('name:"Filter Aktinhalte"')

    if predefined:
        filter_window.send_keys("{LALT}F")

        windows.desktop().find('name:"Kontextmenü"').find(
            f'name:"{predefined}"'
        ).click()

    # Since "Datum bis" has no shortcut in this filter window, we must always
    # navigate to "Datum von" first, and via pressing "Enter" we can then
    # active the "Datum bis" field
    if date_from or date_to:
        filter_window.send_keys("{LALT}D")

        if date_from:
            filter_window.send_keys(f"{date_from}")

        filter_window.send_keys("{ENTER}")

        if date_to:
            filter_window.send_keys(f"{date_to}", send_enter=True)

    # Close filter window
    window().send_keys("{LALT}O")

    # Reload ERV window after filtering
    window().send_keys("{F8}")


def search(term: str) -> None:
    """Perform a text search in the current act.

    Raises:
        AdvokatActManagementSearchError:
            If the "Aktinhalte suchen" window is still open after performing
            the search and pressing "ESC". This indicates that a pop-up
            appeared after the search.
    """

    # Open search window
    window().send_keys("{CTRL}S")
    search_window_locator = 'name:"Aktinhalte suchen"'
    search_window = windows.desktop().find(search_window_locator)

    # Clear previous search text (full text is automatically selected upon
    # opening the search window)
    search_window.send_keys("{BACK}")

    # Enter search term and close window. This should set the focus to the
    # first document matching the search term.
    search_window.send_keys(f"{term}", send_enter=True)
    search_window.send_keys("{ESC}")

    search_window = windows.desktop().find(
        search_window_locator, raise_error=False, timeout=1
    )
    if search_window:
        search_window.send_keys("{ESC}")
        raise _errors.AdvokatActManagementSearchError()


def open_act_master_data() -> windows.WindowElement:
    """Open & return the master data window of the currently selected act."""
    window().send_keys("{F4}")
    return window().find_child_window('subname:"Akt - Stammdaten"')


def open_for_editing() -> windows.WindowElement:
    """Open the currently selected record for editing."""
    menu = window().find('name:"Anwendungsmenü"').find('name:"Bearbeiten"')
    menu.click()

    menu.find('control:MenuItemControl and name:"Ändern"').click()

    return window().find_child_window("control:WindowControl")


def new_entry(entry_type: str) -> None:
    """Open the window for creating a new act entry (document, service, etc).

    Args:
        entry_type:
            Type of the entry to create. Must be a selectable type from the
            Advokat menu "Bearbeiten" > "Neu".
    """
    menu = window().find('name:"Anwendungsmenü"').find('name:"Bearbeiten"')
    menu.click()

    menu.find('control:MenuItemControl and name:"Neu"').click()
    menu.find(f'control:MenuItemControl and name:"{entry_type}"').click()
