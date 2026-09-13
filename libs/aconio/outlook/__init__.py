"""Wrapper library for Robocorp's `RPA.Outlook.Application`.

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
`RPA.Outlook.Application` library through the `app()` function, which
always returns an instance of `RPA.Outlook.Application.Application`:
```python
outlook.start()
outlook.app().get_emails(folder_name="Gesendete Elemente")
```
"""

import os
import time
import typing
import datetime
import functools
import faulthandler

import RPA.application
import RPA.Outlook.Application
import robocorp.windows as windows

import aconio.outlook.types as types
import aconio.outlook.errors as errors

from aconio import utils

# Disable `robocorp.windows` thread warning dumps
faulthandler.disable()

# Typedefs
Any = typing.Any
COMError = RPA.application.COMError
OutlookApp = RPA.Outlook.Application.Application


@functools.lru_cache
def app() -> OutlookApp:
    return OutlookApp()


def start(
    retries: int = 3,
    delay: float = 5,
    minimize: bool = False,
    locator: str | None = None,
) -> None:
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
        locator:
            This parameter can override the default locator for the Outlook
            application. For example can this parameter be used if the client
            has a different language setting in his Outlook application.
    """

    # Quit any Outlook instances that may be open from previous runs to
    # prevent interference with the next application start
    try:
        app().quit_application()
    except:  # pylint: disable=bare-except
        pass

    windows.desktop().windows_run("Outlook")

    outlook_locator = (
        'subname:"Outlook" class:rctrl_renwnd32 > '
        'subname:"Neue E-Mail" class:NetUIRibbonButton'
    )

    if locator:
        outlook_locator = locator

    utils.wait_until_succeeds(
        retries=retries,
        timeout=delay,
        function=windows.desktop().find,
        locator=outlook_locator,
        search_depth=12,
    )

    # Additional wait for Outlook to perform any leftover loading operations
    time.sleep(2)

    # Try to execute the `open_application` function multiple times to avoid
    # server errors
    utils.wait_until_succeeds(
        retries=3,
        timeout=5,
        function=app().open_application,
    )

    if minimize:
        windows.find_window(
            'subname:"Outlook" class:rctrl_renwnd32'
        ).minimize_window()


def send_email(
    subject: str,
    body: str,
    to: str | list[str] | None,
    cc: str | list[str] | None = None,
    bcc: str | list[str] | None = None,
    html_body: bool = False,
    send_as: str | None = None,
    account: str | None = None,
    attachments: list[str] | None = None,
    email_id: str | None = None,
    draft: bool = False,
) -> str:
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
        send_as:
            E-Mail address of the sender account. This uses the default account
            configured in Outlook Desktop to send from the specified e-mail
            address using the "Send As" permission. Cannot be used with the
            `account` parameter.
        account:
            E-Mail address of the sender account. This assumes that the given
            account is available in the Outlook Desktop app with "Full Access"
            permissions and will use this account to send the e-mail. Cannot be
            used with the `send_as` parameter.
        attachments:
            List of filepaths to e-mail attachments.
        email_id:
            An unique id to identify the email object. If not given the
            function creates its own id using the mail
            subject + the current datetime.
        draft:
            If `True`, the e-mail will not be sent and stored in the drafts
            folder. Defaults to `False`.

    Returns:
        str:
            The email_id set on the mail object.
    """
    if not to:
        if draft:
            to = []
        else:
            raise ValueError(
                "Parameter `to` is None even though draft is false!"
            )

    if not attachments:
        attachments = []

    mail = app().app.CreateItem(0)
    mail.To = ";".join(to) if isinstance(to, list) else to
    mail.Subject = subject

    # Define a custom property (Tracking ID) using MAPI Named Property
    if not email_id:
        email_id = str(
            hash(
                (subject, datetime.datetime.now().strftime("%d.%m.%y-%H:%M:%S"))
            )
        )

    mail = _set_custom_property(mail, "EmailID", email_id)

    if cc:
        mail.CC = ";".join(cc) if isinstance(cc, list) else cc

    if bcc:
        mail.BCC = ";".join(bcc) if isinstance(bcc, list) else bcc

    if account and send_as:
        raise ValueError(
            "Parameters `account` and `send_as` cannot be used together!"
        )

    if account:
        acc = get_account_by_email(account)
        _configure_sender_account(mail, acc)

    if send_as:
        # Event though the property is called "SentOnBehalfOfName", this
        # action will force the e-mail to be sent via the "Send As" permission.
        mail.SentOnBehalfOfName = send_as

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

        return email_id
    except COMError as exc:
        raise errors.from_com_error(exc) from exc


def get_account_by_email(account_email: str) -> Any:
    accounts = app().app.Session.Accounts
    for i in range(1, accounts.Count + 1):
        acc = accounts.Item(i)
        if acc.SmtpAddress == account_email:
            return acc
    raise errors.AccountNotFoundError(
        f"Could not find account with e-mail '{account_email}'!"
    )


def _configure_sender_account(mail: Any, account: Any) -> None:
    """Configure the sender account for an Outlook `MailItem`."""

    # Note: Setting the `SendUsingAccount` property on the mail object
    # does not work. For some reason we have to invoke the actual VBA
    # function using the below command.
    # pylint: disable=protected-access
    mail._oleobj_.Invoke(*(64209, 0, 8, 0, account))


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
    folder: Any,
    email_filter: str,
    sort: tuple[str, bool] = None,
) -> list[Any]:
    """Find specific e-mails in an Outlook folder.

    Args:
        folder:
            Outlook folder object. Can be obtained via `get_folder_by_name` or
            `get_folder_by_type`.
        email_filter:
            Outlook filter applied to find the desired E-Mail.
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

    folder_mails = folder.Items

    try:
        mails = folder_mails.Restrict(email_filter)
    except Exception as exc:  # pylint: disable=broad-except
        raise AttributeError(f"Invalid filter '{email_filter}'") from exc

    if not mails:
        return []

    if sort:
        mails.Sort(sort[0], sort[1])

    return mails


def get_email_with_id(folder_type: Any, account: Any, email_id: str) -> Any:
    """
    Return a MailItem from Outlook with a given ID.

    This function uses custom `MAPI` properties to identify an email with an ID.

    Args:
        folder_type:
            The folder type to find the correct folder.
        email_id:
            The set ID of the email.

    Returns:
        Any:
            The email for with given email_id.

    Raises:
        MailNotFoundError:
            If no mail can be found for the given email_id.

    """
    folder = get_folder_by_type(folder_type, account)
    folder_mails = folder.Items

    prop_dasl = "http://schemas.microsoft.com/mapi/string/{00020329-0000-0000-C000-000000000046}/EmailID/0000001f"  # pylint: disable=line-too-long
    email_filter = f"@SQL=\"{prop_dasl}\" = '{email_id}'"

    mail_item = folder_mails.Find(email_filter)

    if not mail_item:
        raise errors.MailNotFoundError(
            f"Could not find E-Mail ID '{email_id}' in folder '{folder}'."
        )

    return mail_item


def get_folder_by_type(
    folder_type: types.FolderType, account_name: str | None = None
) -> Any:
    """Get an Outlook folder by its type.

    Args:
        folder_type:
            Enum value representing the Outlook folder type.

    Returns:
        Any:
            Outlook folder object.

    Raises:
        ValueError:
            If the given `folder_type` cannot be found in Outlook.
    """

    if account_name:
        account = get_account_by_email(account_name)
        folder = account.DeliveryStore.GetDefaultFolder(folder_type.value)
    else:
        folder = app().app.Session.GetDefaultFolder(folder_type.value)

    if not folder:
        msg = f"Failed to obtain folder with type '{folder_type.name}'"

        if account_name:
            msg += f" from account '{account_name}'."
        else:
            msg += "from default account."
        raise errors.FolderNotFoundError(msg)

    return folder


def get_folder_by_name(folder_name: str, account_name: str | None) -> Any:
    """Get an Outlook folder by its name.

    Args:
        folder_name:
            Name of the Outlook folder to search.
        account_name:
            Name of the Outlook account that holds the folder. Not required if
            the desired account is the currently configured default account.

    Returns:
        Any:
            Outlook folder object.

    Raises:
        ValueError:
            If the folder with the given properties cannot be found in Outlook.
    """

    # pylint: disable=protected-access
    folder = app()._get_folder(account_name, folder_name)

    if not folder:
        msg = f"Failed to obtain folder with name '{folder_name}'"

        if account_name:
            msg += f" from account '{account_name}'."
        else:
            msg += "from default account."

        raise errors.FolderNotFoundError(msg)

    return folder


def is_open():
    """Return `True` if the Outlook application is open."""
    if app()._app:  # pylint: disable=protected-access
        return True
    return False


def _set_custom_property(
    mail: Any, property_name: str, property_value: str
) -> Any:

    mail.PropertyAccessor.SetProperty(
        "http://schemas.microsoft.com/mapi/string/{00020329-0000-0000-C000-000000000046}/"  # pylint: disable=line-too-long
        + property_name,
        property_value,
    )

    return mail
