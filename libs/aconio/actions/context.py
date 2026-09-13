"""Provide a context manager for defining actions within a consumer process."""

import enum
import contextlib

import robocorp.workitems

import aconio.actions
from aconio import errors

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

        # Set to 'False' if action should not be marked as completed
        # upon exiting the context manager
        self.autocomplete = True

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return wrapper

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            exc = self._convert_to_automation_error(exc_value)
            action_manager().fail(self.action_name, exc)
        elif not self.autocomplete:
            pass
        else:
            action_manager().complete(self.action_name)

        # Append the action payload to the current work item
        active_work_item = robocorp.workitems.inputs.current
        aconio.actions.append_to_work_item(active_work_item)

        # Return "False" to propagate the exception if any
        return False

    def set_warning(self, message: str) -> None:
        """Mark an action with a warning message.

        This also sets the action state to 'WARNING' and prevents the action
        from being marked as completed when exiting the context manager.
        """
        action_manager().warn(self.action_name, message)
        self.autocomplete = False

    def set_message(self, message: str) -> None:
        """Set a message for the action."""
        action_manager().set_message(self.action_name, message)

    def skip(self) -> None:
        """Mark the action as skipped."""
        action_manager().skip(self.action_name)
        self.autocomplete = False

    def _convert_to_automation_error(
        self, exc: Exception
    ) -> errors.AutomationError:
        """Convert an exception to an automation error."""
        if isinstance(exc, errors.AutomationError):
            return exc

        new_exc = errors.ApplicationError("unexpected automation error")
        new_exc.__cause__ = exc
        return new_exc
