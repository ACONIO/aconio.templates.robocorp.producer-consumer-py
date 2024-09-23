"""A wrapper for Robocorp's `RPA.Outlook.Application` library.

## Features
The following features extend or improve the existing functionality of the
`RPA.Outlook.Application` library:
- A `start` function that wraps the conventional `open_application` function
    and applies improved error-handling mechanisms to avoid `makepy` and `COM`
    errors in multi-user server environments.
- An improved `send_email` function with additional options, such as specifying
    the sender account, or storing the e-mail as a draft.
- A `save_email` function for storing e-mails on the filesystem as `.msg` 
    files.
- A `filter_emails` function for identifying certain e-mails within Outlook.
    
## Usage

The following example starts the Outlook application while handling possible
errors and sends an e-mail. After the e-mail is sent, the `save_email` function
is used to identify the sent e-mail and store it to the filesystem.
```python
import datetime
import win32api
import pywintypes

from aconio import outlook

# Start the outlook application and handle possible errors
outlook.start()

mail_subject = "Test E-Mail"

# Send an e-mail
outlook.send_email(
    to="patrick.krukenfellner@aconio.net",
    cc="matthias.reumann@aconio.net",
    subject=mail_subject,
    body="Test Content"
)

# Give Outlook some time to send the e-mail
time.sleep(5)

# Get a timestamp from one minute ago
curr_datetime = datetime.datetime.now() - datetime.timedelta(minutes=1)

# Bring the date into the 'Short Date' format configured for the current
# Windows user. This is required for the Outlook filter to work properly.
search_date = win32api.GetDateFormat(
    0, 0x00000001, pywintypes.Time(curr_datetime)
)

mail_filter = (
    f\"""[SentOn] > '{search_date} {curr_datetime.strftime("%I:%M %p")}' \"""
    f"And [Subject] = '{mail_subject}'"
)

# Identify the recently sent e-mail
mails = outlook.filter_emails(
    folder_name="Gesendete Elemente",
    email_filter=mail_filter,
)

# Save the e-mail to disk
outlook.save_email(
    mail=mails[1], # Note: Outlook array indices start at 1
    output_file_path="my_email.msg",
)
```

### Outlook Filters
In the above example, an Outlook filter is used to find the recently sent
e-mail via the `SentOn` and `Subject` properties. Outlook filters can get
quite tricky, especially when working with date and time. As you have seen
in the example, we must convert the search date to a correct format using the
`win32api`.

See the following link for more information:
https://learn.microsoft.com/en-us/office/vba/api/outlook.items.restrict#creating-filters-for-the-find-and-restrict-methods


### Using Robocorp's `RPA.Outlook.Application`
If required, you can access the already existing features of the
`RPA.Outlook.Application` library through the `_outlook()` function, which
always returns an instance of `RPA.Outlook.Application.Application`:
```python
outlook.start()
outlook._outlook().get_emails(folder_name="Gesendete Elemente")
```
"""

import os
import time
import functools
import faulthandler

from typing import Any
from robocorp import windows

from RPA.application import COMError
from RPA.Outlook.Application import Application as OutlookApp

from aconio.core import utils

faulthandler.disable()  # Disable robocorp.windows thread warning dumps


@functools.lru_cache  # Always return the same instance.
def _outlook() -> OutlookApp:
    return OutlookApp()


def start(retries: int = 3, delay: float = 5, minimize: bool = False) -> None:
    """Start the Outlook application.

    Add additional error handling capabilities around the `open_application`
    function from `RPA.Outlook.Application` to avoid `makepy` and `COM` errors
    often occuring when using `open_application` simultaneously on different
    user accounts on the same server.

    Args:
        retries:
            Determines how often errors are ignored when trying to find the
            Outlook UI after starting the application. Increase this if Outlook
            takes longer to start on the environment or if your find that `COM`
            and `makepy` errors still occur. Defaults to 3.
        delay:
            Wait time between each retry in seconds. Defauls to 5.
        minimize:
            Automatically minimize the Outlook application after a successful
            start. Defaults to False.
    """

    # Quit any Outlook instances that may be open from previous runs to
    # prevent interference with the next application start
    try:
        _outlook().quit_application()
    except:  # pylint: disable=bare-except
        pass

    windows.desktop().windows_run("Outlook")

    utils.wait_until_succeeds(
        retries=retries,
        timeout=delay,
        function=windows.desktop().find,
        locator=(
            'subname:"Outlook" class:rctrl_renwnd32 > '
            'name:"Neue E-Mail" class:NetUIRibbonButton'
        ),
        search_depth=12,
    )

    # Additional wait for Outlook to perform any leftover loading operations
    time.sleep(2)

    # Try to execute the `open_application` function multiple times to avoid
    # server errors
    utils.wait_until_succeeds(
        retries=3,
        timeout=5,
        function=_outlook().open_application,
    )

    if minimize:
        windows.find_window(
            'subname:"Outlook" class:rctrl_renwnd32'
        ).minimize_window()


def send_email(
    subject: str,
    body: str,
    to: str | list[str],
    cc: str | list[str] = None,
    bcc: str | list[str] = None,
    html_body: bool = False,
    sender: str = None,
    attachments: list[str] = None,
    draft: bool = False,
) -> bool:
    """Send email via Outlook.

    Args:
        subject:
            The e-mail subject.
        body:
            The e-mail body. Must be in HTML format if `html_body` is `True`.
        to:
            String or list of recipient e-mail addresses.
        cc:
            String or list of CC e-mail addresses.
        bcc:
            String or list of BCC e-mail addresses.
        html_body:
            Determine if Outlook will interpret the given `body` as HTML.
            Defaults to `False`.
        sender:
            E-Mail address of the sender account. Note that the default account
            configured in Outlook requires 'Send As' permissions on this
            account.
        attachments:
            List of filepaths to e-mail attachments.
        draft:
            If `True`, the e-mail will not be sent and stored in the drafts
            folder. Defaults to `False`.
    """

    if not attachments:
        attachments = []

    mail = _outlook().app.CreateItem(0)
    mail.To = ";".join(to) if isinstance(to, list) else to
    mail.Subject = subject

    if cc:
        mail.CC = ";".join(cc) if isinstance(cc, list) else cc

    if bcc:
        mail.BCC = ";".join(bcc) if isinstance(bcc, list) else bcc

    if sender:
        # Event though the property is called 'SentOnBehalfOfName', this action
        # requires the default account configured in Outlook to have the
        # 'Send As' permission on the account specified with `sender`, which is
        # different than the 'Send on Behalf' permission
        mail.SentOnBehalfOfName = sender

    if html_body:
        mail.HTMLBody = body
    else:
        mail.Body = body

    for attachment in attachments:
        filepath = os.path.abspath(attachment)

        try:
            mail.Attachments.Add(filepath)
        except COMError as exc:
            raise RuntimeError(
                f"Failed to add attachment '{filepath}' to mail!"
            ) from exc

    # Send mail, or store it as draft
    try:
        if draft:
            mail.Save()
        else:
            mail.Send()
    except COMError as exc:
        raise RuntimeError("Failed to send e-mail due to COMError!") from exc


def save_email(
    mail: Any,
    output_file_path: str,
) -> None:
    """Save an Outlook `MailItem` object to disk.

    Args:
        mail:
            `MailItem` to be saved.
        output_file_path:
            Path to the resulting `.msg` file. Can end with '.msg', otherwise
            it will automatically be appended.

    Raises:
        ValueError:
            If `mail` is not of type `MailItem`.
    """

    if type(mail).__name__ != "_MailItem":
        raise ValueError("Parameter `mail` must be a valid Outlook `MailItem`.")

    if not output_file_path.endswith(".msg"):
        output_file_path = output_file_path + ".msg"

    mail.SaveAs(os.path.abspath(output_file_path))


def delete_email(mail: Any) -> None:
    """Delete an Outlook `MailItem`.

    Note that this only moves the e-mail to the "Gelöschte Elemente" folder.

    Args:
        mail:
            `MailItem` to be deleted.

    Raises:
        ValueError:
            If `mail` is not of type `MailItem`.
    """

    if type(mail).__name__ != "_MailItem":
        raise ValueError("Parameter `mail` must be a valid Outlook `MailItem`.")

    mail.Delete()


def filter_emails(
    folder_name: str,
    email_filter: str,
    account_name: str = None,
    sort: tuple[str, bool] = None,
) -> list[Any]:
    """Find specific e-mails in an Outlook folder.

    Args:
        folder_name:
            Name of the Outlook folder to search.
        email_filter:
            Outlook filter applied to find the desired E-Mail.
        account_name:
            Name of the Outlook account that holds the e-mail. Not required if
            the desired account is the currently configured default account.
        sort:
            Tuple of (`str`, `bool`), where the first item must be an Outlook
            `MailItem` property (including brackets, e.g. '[SentOn]') and the
            second item determines the sorting order. If `True`, results will
            be sorted in descending order, otherwise ascending.
            For example: `("[SentOn]", True)` for retrieving the most recently
            sent `MailItem` first.

    Returns:
        list[Any]:
            List of Outlook mail items.

    Raises:
        AttributeError:
            If the given `email_filter` is invalid.
    """
    # pylint: disable=protected-access
    folder = _outlook()._get_folder(account_name, folder_name)
    folder_mails = folder.Items if folder else []

    try:
        mails = folder_mails.Restrict(email_filter)
    except Exception as exc:  # pylint: disable=broad-except
        raise AttributeError(f"Invalid filter '{email_filter}'") from exc

    if not mails:
        return []

    if sort:
        mails.Sort(sort[0], sort[1])

    return mails


def is_open():
    """Return `True` if the Outlook application is open."""
    if _outlook()._app:  # pylint: disable=protected-access
        return True
    return False
