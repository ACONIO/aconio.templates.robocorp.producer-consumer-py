"""State tracking module for robot runs."""

from __future__ import annotations

import typing
import functools

from aconio.state_tracking._asset import TrackingAsset, TrackingAssetEntry
from aconio.state_tracking._states import States


class StateTracker:
    """State tracking interface for a robot run."""

    def tracked_state(self, name: str) -> TrackedState:
        """Decorator for defining a state tracked by `aconio.state_tracking`."""
        return TrackedState(name=name, tracker=self)

    def configure(
        self, asset_name: str, state_dict: dict[str, int], enabled: bool = True
    ):
        """Configure the state manager.

        Args:
            asset_name:
                The name of the tracking asset in the Control Room.
            state_dict:
                Dictionary for defining the possible progression states.
                The key is the state name and the value is the order
                in which the states are being progressed.
                Example: `{"state_1": 1, "state_2": 2}`
            enabled:
                If the tracker should be active. If `False`, no state
                tracking will be performed and no Control Room asset will be
                loaded. Defaults to `True`.
        """

        self.asset_name = asset_name
        self.available_states = States(state_dict=state_dict)
        self.enabled = enabled

        if self.enabled:
            self.cr_asset = TrackingAsset(
                asset_name=self.asset_name,
                available_states=self.available_states,
            )

        self.loaded_entries = []

    def load(self, tracked_ids: list[str]) -> None:
        """Load the given tracking object IDs into the state tracker.

        Defines which object IDs are currently being tracked. Any state
        tracking action will be performed only for these IDs. IDs that do not
        yet exist in the Control Room asset are created with the lowest
        configured state and immediately persisted.

        Args:
            tracked_ids:
                IDs of the objects to be added to the tracker.
        """
        if not self.enabled:
            return

        self.loaded_entries = [
            self._load_or_create_entry(id_) for id_ in tracked_ids
        ]
        self._verify_all_loaded_states_are_equal()
        self.cr_asset.upsert_many(self.loaded_entries)

    def _load_or_create_entry(self, id_: str) -> TrackingAssetEntry:
        return self.cr_asset.get(id_) or TrackingAssetEntry(
            id_=id_, state=self.available_states.lowest
        )

    def set_state(self, name: str) -> None:
        """Set the state of all currently tracked objects.

        Args:
            name:
                The name of the state to be set.
        """

        if not self.enabled:
            return

        for entry in self.loaded_entries:
            entry.state = self.available_states.get_by_name(name)

        self.cr_asset.upsert_many(self.loaded_entries)

    def get_all_tracker_entries(self) -> list[TrackingAssetEntry]:
        """Get list of all tracker entries, including unloaded ones."""
        return self.cr_asset.entries

    def _verify_all_loaded_states_are_equal(self) -> None:
        if not all(
            e.state == self.loaded_entries[0].state for e in self.loaded_entries
        ):
            raise ValueError(
                "Deviating object states detected! One or more object IDs "
                "registered in state tracking have different states. Please "
                "check the Control Room asset."
            )


class TrackedState:
    """
    A decorator defining the wrapped function as a state tracked by
    `aconio.state_tracking`.
    """

    def __init__(self, name: str, tracker: StateTracker):
        self.name = name
        self.tracker = tracker

    def __call__(self, func: typing.Callable):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            # Since the decorator is applied at import time, we need to
            # delay the state lookup until the function is called, because
            # before that, 'available_states' ist not yet set.
            self.state = self.tracker.available_states.get_by_name(self.name)

            if not self._should_execute_step():
                return

            result = func(*args, **kwargs)
            self.tracker.set_state(self.state.name)

            return result

        return wrapper

    def _should_execute_step(self) -> bool:
        if not self.tracker.enabled:
            return True

        # At this point, we can expect all loaded
        # entries to have the same state.
        loaded_state = self.tracker.loaded_entries[0].state

        if loaded_state is None:
            return True

        if loaded_state < self.state:
            return True

        return False
