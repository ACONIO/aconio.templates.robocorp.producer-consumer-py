"""This module contains commonly used decorators for Robocorp projects."""

import functools

from robocorp import workitems

from aconio.core import errors


def run_function(func):
    """Intercept exceptions and prepare them for Robocorp Control Room.

    Should be used for process `run` functions intended to process a single
    work item.

    Raises:
        `BusinessError` or `AutomationError`:
            Re-raise, if the wrapped function raises one of the above.

        `RuntimeError`:
            If any other exception is raised by the wrapped function, raise a
            RuntimeError with a consise error message. This is due to the fact
            that Robocorp Control Room's character limit for exception messages
            is 1000 chars.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (errors.AutomationError, errors.BusinessError) as e:
            raise e
        except Exception as exc:
            raise RuntimeError("unexpected automation error") from exc

    return wrapper


def attach_reporter(func):
    """Intercept `BusinessError` exceptions and create Reporter work items.

    Should be used for `run` functions of consumer processes.

    Catch `BusinessError` exceptions and create a work item using
    `robocorp.workitems`. Other exception types are re-raised.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except errors.BusinessError as e:
            if e.code:
                item = workitems.inputs.current

                workitems.outputs.create(
                    {
                        "failed_wi_id": item.id,
                        "failed_wi_code": e.code,
                        "failed_wi_payload": item.payload,
                    }
                )

            else:
                raise e

    return wrapper
