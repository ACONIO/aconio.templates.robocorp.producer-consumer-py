"""Specification of the work item passed to Robocorp Control Room."""

import pydantic

import robocorp.log
import robocorp.workitems


class Item(pydantic.BaseModel):
    """A work item created by the Producer and processed by the Consumer."""

    pass


def create_rc_wi_from_pydantic_model(model: pydantic.BaseModel) -> None:
    """Create a Robocorp output work item from a pydantic model."""

    robocorp.log.console_message(
        f"Creating {type(model).__name__}...\n", "stdout"
    )

    # Use Pydantic's JSON-mode dump so date/datetime objects are serialized to
    # ISO 8601 strings and Enums are dumped by value. This ensures the payload
    # is JSON-serializable for Robocorp work items.
    payload = model.model_dump(mode="json")

    robocorp.workitems.outputs.create(payload)
