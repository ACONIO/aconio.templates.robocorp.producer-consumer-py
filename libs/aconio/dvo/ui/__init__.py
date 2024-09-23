"""Handle UI interactions with the DVO application."""

import os
import time
import functools
import faulthandler

from robocorp import windows, log
from pynput_robocorp import keyboard

from RPA.Desktop import Desktop

from aconio.dvo.ui._locators import locators

faulthandler.disable()


@functools.lru_cache
def _desktop() -> Desktop:
    return Desktop()


class DVOError(Exception):
    """DVO related error."""


def dvo_window(**kwargs) -> windows.WindowElement:
    """Return the main DVO window."""
    return windows.find_window("id:uiMain", **kwargs)


def open_application(path: str | None = None) -> None:
    """Open the DVO application.

    Args:
        path:
            Path to the DVO `.exe` file.
            Defaults to `C:\\dvo32\\dvoNet\\App\\Studio\\Studio.exe`.
    """
    if not path:
        path = os.path.join(
            "c:", os.sep, "dvo32", "dvoNet", "App", "Studio", "Studio.exe"
        )

    windows.desktop().windows_run(path)

    # Wait for the login window to verify that DVO opened properly
    try:
        windows.find_window("id:uiAnmeldung", timeout=15)
    except windows.ElementNotFound as e:
        raise DVOError(
            "Failed to detect login window after opening DVO!"
        ) from e


def close_application() -> None:
    """Close the DVO application."""
    try:
        dvo_window().find('name:"Schließen"').click()

        close_app_popup = windows.desktop().find(
            'name:"Programm beenden"', raise_error=False, timeout=4
        )

        if close_app_popup is not None:
            close_app_popup.find('name:"Ja" and class:Button').click()

    except windows.ElementNotFound:
        log.warn("Failed to close DVO app, trying to force kill it")
        dvo_window().close_window()


def is_open() -> bool:
    """Return `True` if DVO is running, otherwise return `False`."""
    return dvo_window(raise_error=False) is not None


def login(
    username: str,
    password: str,
    timeout: float = 10,
    handle_popups: bool = True,
) -> None:
    """Login to the DVO application.

    Args:
        username:
            DVO username.
        password:
            DVO password.
        timeout:
            Time in seconds to wait for the DVO window to load after login.
        handle_popups:
            Wait for time tracking and user sync pop-ups and handle them if
            they appear. Can be disabled if pop-ups are not expected to save
            time. Release notes are always handeled, regardless of this
            setting, since they can appear any time. Defaults to `True`.
    """

    try:
        _enter_credentials(
            username=username, password=password, timeout=timeout
        )
    except DVOError:
        # Check if user is already logged in at another workstation
        login_failed = windows.find_window("id:uiAnmeldung").find(
            'name:"Anmeldung fehlgeschlagen"'
        )
        log.warn("First DVO login failed, user already logged in!")

        login_failed.find('name:"OK" class:Button').click()

        # Try to release DVO users before login
        log.warn("Releasing users and trying to login again!")
        release_users()
        _enter_credentials(
            username=username, password=password, timeout=timeout
        )

    # Handle possible pop-ups
    if handle_popups:
        if time_popup := dvo_window().find_child_window(
            "id:uiSelectTime", timeout=5, raise_error=False
        ):
            time_popup.find('name:"Abbrechen"').click()

        sync_popup = dvo_window().find(
            'subname:"Eine Synchronisation"', timeout=5, raise_error=False
        )
        if sync_popup:
            sync_popup.get_parent().find('name:"OK" and class:Button').click()

    # Handle release notes
    if release_notes := dvo_window().find(
        "id:uiReleasenotes", timeout=5, raise_error=False
    ):
        release_notes.log_screenshot()
        log.info("A release notes popup appeared after opening DVO, closing it")
        release_notes.find("id:cmdCancel").click()


def release_users() -> None:
    """Release all logged-in DVO users from the login screen.

    Using a keyboard shortcut & a click on the blue icon of the DVO login
    window, you can get a list of currently logged in users. From there, a
    user can be released, which is helpful if you cannot login with a user
    due to it being logged in on another workstation.

    Users often still appear as "logged in" if the DVO application was
    unexpectedly quit in a previous session. In those scenarios, the user
    must always be released first, before it can be logged in again.
    """
    # Note: the locator must be identified before the `with` - for some reason
    # it does not hold down the two keys if find() is called during the `with`
    login_pic = windows.find_window("id:uiAnmeldung").find("id:picLogin")
    with keyboard.Controller().pressed(keyboard.Key.ctrl, keyboard.Key.shift):
        login_pic.click()

    time.sleep(2)  # Wait for the user list to load

    # Select all users
    windows.desktop().send_keys("{SHIFT}{END}")

    # Click "Freigeben", wait and then click "Schließen"
    user_list = windows.find_window("id:uiAnmeldung").find("id:uiUserList")
    user_list.find("id:cmdReset").click()
    time.sleep(3)
    user_list.find("id:cmdClose").click()


def navbar_open(
    category: str, item: str | None = None, locator: str | None = None
) -> None:
    """Open an element of the DVO navbar on the left side.

    Args:
        category:
            Name of the navbar category (e.g. "Favoriten").
        item:
            Name of the navbar item within the category (e.g. "Dokumente").
            Note: This implicitly uses the `name` locator from robocorp.windows
            thus the name must match exactly. Use `locator` for more complex
            methods of locating the navbar item.
        locator:
            Can be used instead of `item`. Full locator for robocorp.windows to
            identify the navbar item.

    Raises:
        ValueError: If both item and locator are unset, or both are set.
    """

    if item is None and locator is None:
        raise ValueError("Either `item` or `locator` must be set.")
    elif item is not None and locator is not None:
        raise ValueError(
            "Both `item` or `locator` cannot be set. Use either of them."
        )

    if not locator:
        locator = f'name:"{item}"'

    dvo_window().find(f'name:"{category}"').find(locator).click()


def clear_all_filters() -> None:
    """Clear all currently applied filters in a DVO table view.

    Note: Can only be used if a 'clear all filters' button is currently
    visible on screen.
    """
    _desktop().click(locators().clear_filters)


def set_filter(
    group: windows.ControlElement,
    name: str,
    value: str,
    load_time: float = 2,
    clear_filters: bool = True,
) -> None:
    """Set a column filter in DVO table views.

    Use `set_filters` for setting multiple filters.

    Args:
        group:
            UI element of the DVO group wrapping the table view. See library
            documentation for more information about table views and groups.
        name:
            Name of the colum to filter (e.g. "Betriebsnummer").
        value:
            Value to which the filter will be set.
        load_time:
            Time to wait after the filter has been set (in seconds).
            Defaults to 2.
        clear_filters:
            Clears all existing filters before setting the new filter.
    """

    if clear_filters:
        clear_all_filters()

    # AutomationID '-1' represents the filter row
    # From there, row ID's of the actual table data start with 0
    filter_row = group.find("control:DataItemControl and id:-1")
    filter_row.find(f'name:"{name}"').set_value(value, enter=True)

    time.sleep(load_time)


def set_filters(
    group: windows.ControlElement,
    filters: dict[str, str],
    load_time: float = 2,
    clear_filters: bool = True,
) -> None:
    """Set multiple column filters in DVO table views.

    Use `set_filter` for setting a single filter.

    Args:
        group:
            UI element of the DVO group wrapping the table view. See library
            documentation for more information about table views and groups.
        filters:
            Key/value pairs of column names and their respective filter values.
            Example: `{"Betriebsnummer": "99999"}`
        load_time:
            Time to wait after one filter has been applied. Defaults to 2.
        clear_filters:
            Clears all existing filters before setting the new filters.
    """

    if clear_filters:
        clear_all_filters()

    for col, val in filters.items():
        set_filter(
            group=group,
            name=col,
            value=val,
            load_time=load_time,
            clear_filters=False,
        )


def get_rows(group: windows.ControlElement) -> list[windows.ControlElement]:
    """Return all visible rows in a DVO table view (excluding header).

    Args:
        group:
            UI element of the DVO group wrapping the table view. See library
            documentation for more information about table views and groups.

    Returns:
        List of currently visible DVO data rows.
    """
    rows = group.find_many(
        locator='control:"DataItemControl"', search_strategy="all"
    )

    # Filter header row and return
    return [r for r in rows if r.automation_id != "-1"]


def select_all_rows(group: windows.ControlElement) -> None:
    """Select all rows within a DVO table view.

    Args:
        group:
            UI element of the DVO group wrapping the table view. See library
            documentation for more information about table views and groups.
    """
    get_rows(group=group)[0].click()  # select the first row

    # expand selection to last row
    dvo_window().send_keys("{SHIFT}{CONTROL}{END}")


def select_tab(name: str, load_time: float = 1) -> None:
    """Select a tab from the DVO main tab bar.

    Note that the given tab name must already be open. This function cannot
    open new tabs.

    Args:
        name:
            Name of the DVO tab.
        load_time:
            Time to wait after the filter has been set (in seconds).
            Defaults to 1.
    """

    dvo_window().find(
        f'control:TabItemControl and name:"{name}"',
        search_depth=2,  # ensure that only the main tabs are found
    ).click()

    time.sleep(load_time)


def close_tab(name: str | None = None) -> None:
    """Close a DVO tab.

    Args:
        name:
            If specified, the tab with the given name will first be selected
            before it is closed. Otherwise the current tab will be closed.
    """
    if name:
        select_tab(name)

    dvo_window().find('name:"TabCloseButton"').click()


def find_task(filters: dict[str, str]) -> windows.ControlElement:
    """Find a DVO "Aufgabe" and ensure it is the only one in the table view.

    It is expected that this function is executed while in the DVO main view,
    without the "Aufgaben" tab already being open. Furthermore, the "Aufgaben"
    navbar item must be added to "Favoriten".

    Args:
        filters:
            Key/value pairs of DVO "Aufgaben" view column names and filter
            values to identify the correct "Aufgabe". Example column names
            are: 'Betriebsnummer', 'Periode', 'Aufgabeart'.

    Raises:
        DVOError:
            If multiple tasks or no tasks are listed after applying the given
            filters.

    Returns:
        The identified task row within the "Aufgaben" table view.
    """
    navbar_open(category="Favoriten", locator='subname:"Aufgaben"')
    group = dvo_window().find("id:uiAufgabenliste").find('id:"Data Area"')

    set_filters(group=group, filters=filters)

    rows = get_rows(group=group)

    if len(rows) > 1:
        raise DVOError(
            "More than one task left after applying filers! "
            f"Visible task rows after applying filters: {rows}"
        )
    elif len(rows) < 1:
        raise DVOError("Could not find task matching given filters!")

    # Open & Complete task
    return rows[0]


def open_task(filters: dict[str, str]) -> windows.WindowElement:
    """Find a DVO "Aufgabe" and open it.

    It is expected that this function is executed while in the DVO main view,
    without the "Aufgaben" tab already being open. Furthermore, the "Aufgaben"
    navbar item must be added to "Favoriten".

    Args:
        filters:
            Key/value pairs of DVO "Aufgaben" view column names and filter
            values to identify the correct "Aufgabe". Example column names
            are: 'Betriebsnummer', 'Periode', 'Aufgabeart'.

    Raises:
        DVOError:
            If multiple tasks or no tasks are listed after applying the given
            filters.

    Returns:
        The task tab window element.
    """
    task_row = find_task(filters=filters)
    task_row.double_click(wait_time=2)

    return dvo_window().find_child_window("id:uiAufgabDetail")


def forward_task(
    filters: dict[str, str], responsible_area: str, test_mode: bool = False
) -> windows.WindowElement:
    """Find a DVO "Aufgabe" and forward it to another employee.

    It is expected that this function is executed while in the DVO main view,
    without the "Aufgaben" tab already being open. Furthermore, the "Aufgaben"
    navbar item must be added to "Favoriten".

    Args:
        filters:
            Key/value pairs of DVO "Aufgaben" view column names and filter
            values to identify the correct "Aufgabe". Example column names
            are: 'Betriebsnummer', 'Periode', 'Aufgabeart'.
        responsible_area:
            Value entered in the 'Betreuung' field. DVO will then assign the
            respective employee responsible for that area
            (e.g. 'Bilanzierung').
        test_mode:
            If `True`, the whole action will be performed as usual, but after
            setting the responsible area, the "Speichern & Schließen" button
            will only be hovered over instead of clicked.

    Raises:
        DVOError:
            If multiple tasks or no tasks are listed after applying the given
            filters.

    Returns:
        The task tab window element.
    """
    task_window = open_task(filters=filters)

    task_window.find("id:cboBetreuung").set_value(responsible_area)

    save_btn = task_window.find('name:"Speichern  Schließen"')
    if test_mode:
        save_btn.mouse_hover()
        time.sleep(5)
        close_tab()

        dvo_window().find('name:"Änderungen speichern"').find(
            'name:"Nein" and class:"Button"'
        ).click()

    else:
        save_btn.click()

    close_tab()


def complete_task(filters: dict[str, str], test_mode: bool = False) -> None:
    """Find a DVO "Aufgabe" and mark it as "erledigt".

    It is expected that this function is executed while in the DVO main view,
    without the "Aufgaben" tab already being open. Furthermore, the "Aufgaben"
    navbar item must be added to "Favoriten".

    Args:
        filters:
            Key/value pairs of DVO "Aufgaben" view column names and filter
            values to identify the correct "Aufgabe". Example column names
            are: 'Betriebsnummer', 'Periode', 'Aufgabeart'.
        test_mode:
            If `True`, the whole action will be performed as usual, but upon
            instead of completing the task, the respective button will only be
            highlighted instead of clicked.

    Raises:
        DVOError:
            If multiple tasks or no tasks are listed after applying the given
            filters.
    """

    task_row = find_task(filters=filters)
    task_row.right_click(wait_time=3)

    if test_mode:
        _desktop().highlight_elements(locators().complete_task)
    else:
        _desktop().click(locators().complete_task)

    # Wait for the task to be properly completed
    time.sleep(2)

    close_tab()


def open_task_attachment_menu(filters: dict[str, str]) -> windows.WindowElement:
    """Find a DVO "Aufgabe" and open the attached document menu.

    For opening the actual document attached to the task, use
    `open_task_attachment`.

    It is expected that this function is executed while in the DVO main view,
    without the "Aufgaben" tab already being open. Furthermore, the "Aufgaben"
    navbar item must be added to "Favoriten".

    Args:
        filters:
            Key/value pairs of DVO "Aufgaben" view column names and filter
            values to identify the correct "Aufgabe". Example column names
            are: 'Betriebsnummer', 'Periode', 'Aufgabeart'.

    Raises:
        DVOError:
            If multiple tasks or no tasks are listed after applying the given
            filters.

    Returns:
        The attachment menu window element.
    """
    task_row = find_task(filters=filters)
    task_row.right_click(wait_time=3)

    _desktop().click(locators().open_attachment)

    return dvo_window().find_child_window("id:uiDokument")


def open_task_attachment(filters: dict[str, str]) -> None:
    """Find a DVO "Aufgabe" and open the attached document.

    This opens the actual document attached to the DVO task with the according
    application defined on the system for opening documents of that type. For
    only opening the DVO menu of the attached document, use
    `open_task_attachment_menu`.

    It is expected that this function is executed while in the DVO main view,
    without the "Aufgaben" tab already being open. Furthermore, the "Aufgaben"
    navbar item must be added to "Favoriten".

    Args:
        filters:
            Key/value pairs of DVO "Aufgaben" view column names and filter
            values to identify the correct "Aufgabe". Example column names
            are: 'Betriebsnummer', 'Periode', 'Aufgabeart'.

    Raises:
        DVOError:
            If multiple tasks or no tasks are listed after applying the given
            filters.
    """

    attachment_menu = open_task_attachment_menu(filters=filters)

    dok_group = attachment_menu.find('name:"Dokument" and control:GroupControl')

    dok_group.find('name:"Anzeigen" and control:DataItemControl').click()


def upload_task_attachment_to_teamwork(
    filters: dict[str, str], upload_name: str, test_mode: bool = False
) -> None:
    """Find a DVO "Aufgabe" perform a Teamwork upload for the attachment.

    This opens the actual document attached to the DVO task with the according
    application defined on the system for opening documents of that type. For
    only opening the DVO menu of the attached document, use
    `open_task_attachment_menu`.

    It is expected that this function is executed while in the DVO main view,
    without the "Aufgaben" tab already being open. Furthermore, the "Aufgaben"
    navbar item must be added to "Favoriten".

    Args:
        filters:
            Key/value pairs of DVO "Aufgaben" view column names and filter
            values to identify the correct "Aufgabe". Example column names
            are: 'Betriebsnummer', 'Periode', 'Aufgabeart'.
        upload_name:
            How the uploaded document should be named (value entered in
            "Auswertung" field when uploading to Teamwork).
        test_mode:
            If `True`, the whole action will be performed as usual, but instead
            of performing the Teamwork upload at the end, the respective upload
            button will only be highlighted and the changes will be discarded.

    Raises:
        DVOError:
            If multiple tasks or no tasks are listed after applying the given
            filters.
    """

    attachment_menu = open_task_attachment_menu(filters=filters)

    # Teamwork upload menu takes some time to load
    attachment_menu.find('name:"Upload Teamwork"').click(wait_time=15)

    teamwork_menu = attachment_menu.find("id:uiTeamworkUpload")
    teamwork_menu.find("id:cmdSelectFolder").click(wait_time=2)
    teamwork_menu.find('id:uiTeamworkStruktur > name:"Bilanz"').click()
    teamwork_menu.find('id:uiTeamworkStruktur > name:"Übernehmen"').click(
        wait_time=4
    )
    teamwork_menu.find("id:txtAuswertungTW").send_keys(upload_name)

    btn_upload = teamwork_menu.find("id:btnHochladen")
    if test_mode:
        btn_upload.mouse_hover()
        time.sleep(5)

        teamwork_menu.find("id:btnAbbrechen").click()

        attachment_menu.close_window(
            use_close_button=True,
            close_button_locator='name:"Schließen" and control:ButtonControl',
        )

    else:
        btn_upload.click()

    close_tab()


def save_task_attachment(filters: dict[str, str], filepath: str) -> None:
    """Find a DVO "Aufgabe", open the attached document and save it.

    It is expected that this function is executed while in the DVO main view,
    without the "Aufgaben" tab already being open. Furthermore, the "Aufgaben"
    navbar item must be added to "Favoriten".

    Alos, the default document reader must be Microsoft Edge and the default
    print setting (after pressing "CTRL + P") must be "Save as PDF".

    After the document has been saved, the document read and "Aufgaben" tab
    will be closed.

    Args:
        filters:
            Key/value pairs of DVO "Aufgaben" view column names and filter
            values to identify the correct "Aufgabe". Example column names
            are: 'Betriebsnummer', 'Periode', 'Aufgabeart'.
        filepath:
            Path under which the document will be stored.

    Raises:
        DVOError:
            If multiple tasks or no tasks are listed after applying the given
            filters.
    """

    open_task_attachment(filters=filters)

    edge = windows.desktop().find_window(
        'regex:".*Microsoft.*Edge.*" and control:WindowControl'
    )

    # Open print dialogue and save the file as PDF
    edge.send_keys("{CONTROL}P")
    edge.find('name:"Drucken" and class:RootView').find(
        'name:"Speichern" and control:ButtonControl', search_depth=12
    ).click(
        wait_time=4
    )  # Wait for save_as window to appear

    save_window = edge.find('name:"Speichern unter"')
    save_window.find('name:"Dateiname:" and class:AppControlHost').send_keys(
        filepath
    )
    save_window.find('name:"Speichern" and class:Button').click()

    edge.close_window()

    dvo_window().find_child_window("id:uiDokument").close_window(
        use_close_button=True,
        close_button_locator='name:"Schließen" and control:ButtonControl',
    )

    close_tab()


def track_service(
    client_number: str,
    year: str,
    activity_id: str,
    text: str,
    employee_number: str | None = None,
    amount: int = 1,
    test_mode: bool = False,
) -> None:
    """Perform a "Leistungserfassung" in DVO.

    It is expected that this function is executed while in the DVO main view,
    without the "Aufgaben" tab already being open. Furthermore, the "Aufgaben"
    navbar item must be added to "Favoriten".

    Args:
        client_number:
            Value for field "Betrieb".
        employee_number:
            Value for field "Mitarbeiter". Can be `None` if employee is
            already pre-selected.
        year:
            Value for field "Jahr".
        activity_id:
            Value for field "Tätigkeit".
        text:
            Value for field "Text".
        amount:
            Value for field "Anzahl".
        test_mode:
            If `True`, the whole action will be performed as usual, but instead
            of saving the "Leistung", the "Speichern" button will only be
            hovered over and the "Leistung" will be discarded afterwards.

    """

    navbar_open(category="Favoriten", item="Leistungen")

    dvo_window().find("id:uiLeistungenNeu").find('id:"Data Area"').right_click()

    dvo_window().send_keys("{DOWN}")
    dvo_window().send_keys("{ENTER}")

    # The window for tracking a new service has a very long internal load time,
    # hence the find() could case COM errors, which is why we use time.sleep()
    # here
    time.sleep(4)
    service_window = dvo_window().find("id:ucLeistungDetail")
    input_area = service_window.find("id:pnlInput")

    input_area.find("id:cboBetriebNr_EmbeddableTextBox").set_value(
        client_number
    )

    # For some reason, set_value() does not work on the "year" field, so we're
    # manually removing the previous value and setting the desired one
    year_field = input_area.find("id:mtxPeriode")
    year_field.double_click()  # CTRL + A doesn't work in this field
    year_field.send_keys("{back}")
    year_field.send_keys(year)
    year_field.send_keys("{enter}")

    input_area.find("id:cboTaetigkeitNr").set_value(activity_id)

    if employee_number:
        input_area.find("id:cboMitarbeiterNr").set_value(employee_number)

    # Click "increase value" button of the "Anzahl" combobox `amount` times,
    # because `set_value` or `select` does not work on this input field
    for _ in range(amount):
        input_area.find("id:numAnzahl").find('name:"Nach oben"').click(
            wait_time=0.2
        )

    input_area.find("id:txtText").set_value(text)

    save_btn = service_window.find("id:cmdAccept")
    if test_mode:
        save_btn.mouse_hover()
        time.sleep(3)

        # Click "Schließen" and accept the warning pop-up
        service_window.find("id:cmdCanel").click()

        dvo_window().find('name:"Speichern"').find(
            'name:"Nein" and class:"Button"'
        ).click()

    else:
        save_btn.click()

        vollmacht_popup = dvo_window().find(
            'subname:"ERLEA Vollmacht fehlt"', raise_error=False, timeout=2
        )
        if vollmacht_popup:
            log.warn('Detected "ERLEA Vollmacht" pop-up!')
            vollmacht_popup.find('name:"OK" and class:Button').click()

        verrechnung_pop_up_txt = dvo_window().find(
            'subname:"Die Verrechnung der Leistungen"',
            raise_error=False,
            timeout=2,
        )

        if verrechnung_pop_up_txt:
            log.warn('Detected "Verrechnung der Leistungen" pop-up!')
            verrechnung_pop_up_txt.get_parent().find(
                'name:"OK" and class:Button'
            ).click()

    close_tab()


def _enter_credentials(
    username: str, password: str, timeout: float = 10
) -> None:
    """Enter DVO login credentials and click "Anmelden".

    Args:
        username:
            DVO username.
        password:
            DVO password.
        timeout:
            Time in seconds to wait for the DVO window to load after login.

    Raises:
        DVOError:
            If the "Favoriten" section could not be identified after the DVO
            login was performed. This indicates that the login did not work.
    """

    login_window = windows.find_window("id:uiAnmeldung")
    login_window.find("id:txtUsername").set_value("")  # Clear field
    login_window.find("id:txtUsername").send_keys(username)
    login_window.find("id:txtPassword").set_value("")  # Clear field
    login_window.find("id:txtPassword").send_keys(password)
    login_window.find("id:cmdAccept").click()

    # Wait for the DVO window to verify that the login was successful
    try:
        dvo_window(timeout=timeout).find("name:Favoriten")
    except windows.ElementNotFound as e:
        raise DVOError("Failed to perform DVO login!") from e
