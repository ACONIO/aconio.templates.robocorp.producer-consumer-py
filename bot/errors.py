"""This file holds automation errors that will be automatically recognized by the
Robocorp Work Items library and the work item will be marked with the correct
exception type."""

from robocorp.workitems import ApplicationException, BusinessException


class AutomationError(Exception):
    """Base class for all automation errors. This base class
    allows for catching all automation errors, regardless of
    whether they are application or business errors.
    """


class ApplicationError(AutomationError, ApplicationException):
    """Base class for all application errors. Application errors
    are errors that are usually transient. A work item being
    processed when such an error occurs can be retried.
    """


class BusinessError(AutomationError, BusinessException):
    """Base class for all business errors. Business errors are
    errors that are usually permanent. A work item being
    processed when such an error occurs should not be retried
    and likely needs to be corrected.
    """
