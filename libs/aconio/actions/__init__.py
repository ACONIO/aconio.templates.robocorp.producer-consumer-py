"""Provide an interface for tracking actions of the Consumer process."""

from __future__ import annotations

import enum
import functools

import robocorp.workitems

from aconio import errors


class ActionState(enum.StrEnum):
    """State of an action performed by the Consumer."""

    NOT_STARTED = "NOT_STARTED"
    SKIPPED = "SKIPPED"
    WARNING = "WARNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class Action:
    """Information about an action performed by the Consumer."""

    name: str

    description: str
    """
    Description of the action in a few words.
    Makes it easier to use the action for process reports later.
    """

    state: ActionState = ActionState.NOT_STARTED

    error: errors.AutomationError | None = None
    """Set if an error occured while processing the action."""

    message: str | None = None
    """Useful for arbitrary messages that are not errors."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def to_dict(self):
        """Return the action as a dictionary."""

        error = None
        if self.error:
            error = {
                "type": type(self.error).__name__,
                "message": (
                    self.error.message
                    if hasattr(self.error, "message")
                    else str(self.error)
                ),
                "code": (
                    self.error.code if hasattr(self.error, "code") else None
                ),
            }

        return {
            "name": self.name,
            "description": self.description,
            "state": self.state,
            "error": error,
            "message": self.message,
        }

    @classmethod
    def from_dict(cls, d: dict) -> Action:
        """Create an action from a dictionary."""
        action = Action(name=d["name"], description=d["description"])
        action.state = ActionState(d["state"])
        action.message = d.get("message")

        if d["error"]:
            error = getattr(errors, d["error"]["type"])(
                message=d["error"]["message"],
                code=d["error"]["code"],
            )
            action.error = error

        return action


class _ActionManager:
    """Manage all actions of the consumer."""

    _actions: list[Action]
    """List of all actions of the consumer."""

    @staticmethod
    def _requires_initialization(func):
        """Decorator to ensure the action manager is initialized."""

        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # pylint: disable=protected-access
            if not hasattr(self, "_actions") or self._actions is None:
                raise RuntimeError(
                    "ActionManager not initialized. Call initialize() "
                    f"before {func.__name__}()."
                )
            return func(self, *args, **kwargs)

        return wrapper

    def initialize(self, actions: dict[str, str] | type[enum.Enum]) -> None:
        """Initialize the action list with the given action names.

        Args:
            action_names:
                Dictionary of action names and their descriptions.
                If an `enum.StrEnum` class is passed, the enum keys are
                used as action names and the values as descriptions.
                Example:
                `{
                "OPEN_DOCUMENT" : "Dokument öffnen",
                "SAVE_DOCUMENT": "Dokument speichern"
                }`
        """
        if isinstance(actions, type) and issubclass(actions, enum.StrEnum):
            self._actions = [
                Action(name=action.name, description=action.value)
                for action in actions
            ]
        else:
            self._actions = [
                Action(name=name, description=description)
                for name, description in actions.items()
            ]

    @_requires_initialization
    def reset(self) -> None:
        """Reset the action states to begin tracking a new work item."""

        # We re-initialize the actions list with the same action names,
        # thereby dropping the previous state of the actions.
        actions = {a.name: a.description for a in self._actions}
        self.initialize(actions)

    @_requires_initialization
    def complete(self, action: str | enum.Enum) -> None:
        """Mark an action as completed."""
        self._get_action(action).state = ActionState.SUCCESS

    @_requires_initialization
    def skip(self, action: str | enum.Enum) -> None:
        """Mark an action as skipped."""
        self._get_action(action).state = ActionState.SKIPPED

    @_requires_initialization
    def fail(
        self,
        action: str | enum.Enum,
        error: errors.AutomationError,
    ) -> None:
        """Mark an action as failed."""
        action = self._get_action(action)
        action.state = ActionState.FAILED
        action.error = error

    @_requires_initialization
    def warn(self, action: str | enum.Enum, message: str) -> None:
        """Mark an action with a warning message."""
        action = self._get_action(action)
        action.state = ActionState.WARNING
        action.message = message

    @_requires_initialization
    def set_message(self, action: str | enum.Enum, message: str) -> None:
        """Set a message for the action."""
        action = self._get_action(action)
        action.message = message

    def _get_action(self, action: str | enum.Enum) -> Action:
        """Return the action with the given identifier."""

        name = action.name if isinstance(action, enum.Enum) else action

        for action_item in self._actions:
            if action_item.name == name:
                return action_item

        raise ValueError(
            f"Action '{name}' not found. Did you call initialize()?"
        )

    @_requires_initialization
    def to_dict(self) -> dict:
        """Return the action list holding the actions as dictionaries."""
        return [a.to_dict() for a in self._actions]


@functools.lru_cache
def action_manager() -> _ActionManager:
    return _ActionManager()


def append_to_work_item(item: robocorp.workitems.Input) -> None:
    """Append the current actions list to the payload of the given item."""
    item.payload["actions"] = action_manager().to_dict()
    item.save()
