"""This module holds various exception types for Robocorp projects.

The contained exceptions will be automatically recognized by the
`robocorp.workitems` library. As a result of raising on of the exceptions,
the work item will be marked with the correct exception type in Robocorp Control
Room.
"""

from robocorp import workitems


class AutomationError(Exception):
    """Base class for all automation errors.

    This base class allows for catching all automation errors,
    regardless of whether they are application or business errors.
    """


class ApplicationError(AutomationError, workitems.ApplicationException):
    """Base class for all application errors.

    Application errors are errors that are usually transient. A work
    item being processed when such an error occurs can be retried.
    """


class BusinessError(AutomationError, workitems.BusinessException):
    """Base class for all business errors.

    Business errors are errors that are usually permanent. A work
    item being processed when such an error occurs should not be
    retried and likely needs to be corrected.
    """
