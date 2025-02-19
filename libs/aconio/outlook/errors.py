"""Errors for `aconio.outlook` module."""


class OutlookError(Exception):
    """Base class for exceptions in `aconio.outlook`."""


class InvalidRecipientsError(OutlookError):
    """
    Raised upon the following Outlook error message when sending an email:
    'Outlook kennt mindestens einen Namen nicht.'
    """


class FolderNotFoundError(OutlookError):
    """
    Raised when a folder with the given name is not found under the given
    account in the Outlook.
    """


class AccountNotFoundError(OutlookError):
    """
    Raised when an Outlook account with the given name is not found.
    """


class MailNotFoundError(OutlookError):
    """Raised when an email can not be found."""


def from_com_error(com_error: Exception) -> OutlookError:
    """Convert a COM error to a respective `OutlookError`.

    Returns:
        A respective subclass of `OutlookError`, based on the COM error
        message. If the COM error is not recognized, a generic `OutlookError`
        is returned.
    """

    message = _get_com_error_message(com_error)

    if "Outlook kennt mindestens einen Namen nicht." in message:
        return InvalidRecipientsError(
            "Invalid E-Mail Address in recipients list."
        )

    return OutlookError(f"COM error: {message}")


def _get_com_error_message(com_error: Exception) -> str:
    return com_error.excepinfo[2]
