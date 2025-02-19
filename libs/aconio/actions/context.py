"""Provide a context manager for defining actions within a consumer process."""

import enum
import contextlib

import robocorp.workitems

import aconio.actions
import aconio.errors as errors

# Typedefs
action_manager = aconio.actions.action_manager


# pylint: disable=invalid-name
class action(contextlib.ContextDecorator):
    """Context manager for an action.

    Used to wrap a block of code that represents a single action. If the code
    executes without raising an exception, the action is marked as completed.
    If an exception is raised, the action is marked as failed.

    Note that the given action name must match one of the action names defined
    in the action manager.
    """

    def __init__(self, action_name: str | enum.Enum):
        """Initialize the action context manager.

        Args:
            action_name:
                The name of the action to be executed.
                If an enum is given, the enum key is used as the action name.
        """

        if isinstance(action_name, enum.Enum):
            action_name = action_name.name

        self.action_name = action_name

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return wrapper

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            exc = self._convert_to_automation_error(exc_value)
            action_manager().fail(self.action_name, exc)
        else:
            action_manager().complete(self.action_name)

        # Append the action payload to the current work item
        active_work_item = robocorp.workitems.inputs.current
        aconio.actions.append_to_work_item(active_work_item)

        # Return "False" to propagate the exception if any
        return False

    def _convert_to_automation_error(
        self, exc: Exception
    ) -> errors.AutomationError:
        """Convert an exception to an automation error."""
        if isinstance(exc, errors.AutomationError):
            return exc

        new_exc = errors.ApplicationError("unexpected automation error")
        new_exc.__cause__ = exc
        return new_exc
