"""Errors for FinanzOnline interactions."""


class FinanzOnlineError(Exception):
    """Base class for FinanzOnline errors."""

    pass


class PersonificationRequiredError(FinanzOnlineError):
    """
    Raised when a "Personifizierung" dialog shows
    after logging in to FinanzOnline.
    """

    pass


class RepaymentRequestError(FinanzOnlineError):
    """
    Raised when the repayment request cannot be created.
    """

    pass


class TaxAccountQueryError(FinanzOnlineError):
    """Exception raised when the tax account query returns an error."""

    pass


class TaxAccountParsingError(FinanzOnlineError):
    """Exception raised when the tax account data cannot be parsed."""

    pass
