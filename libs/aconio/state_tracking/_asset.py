"""Robocorp Control Room state tracking asset."""

from __future__ import annotations

import pydantic
import robocorp.storage

from aconio.state_tracking._states import State, States


class TrackingAssetEntry(pydantic.BaseModel):
    """An entry within the Robocorp Control Room state tracking asset."""

    model_config = pydantic.ConfigDict(coerce_numbers_to_str=True)

    id_: str
    """ID of the entity to be tracked (e.g. a BMD "Frist" or a "Aufgabe")."""

    state: State | None = None
    """State of the entity to be tracked."""


class TrackingAsset:
    """A Control Room for tracking processing states of robot run objects."""

    def __init__(self, asset_name: str, available_states: States):
        self.asset_name = asset_name
        self.available_states = available_states

        self.entries = []
        self.load()

    def get(self, id_: str) -> TrackingAssetEntry | None:
        """Get an entry by its ID."""

        id_ = str(id_)

        for entry in self.entries:
            if entry.id_ == id_:
                return entry

        return None

    def append(self, entry: TrackingAssetEntry) -> None:
        """Append a single entry to the asset."""

        self.entries.append(entry)
        self._update_asset()

    def upsert(self, entry: TrackingAssetEntry) -> None:
        """Create or update an entry."""
        self.upsert_many([entry])

    def upsert_many(self, entries: list[TrackingAssetEntry]) -> None:
        """Create or update multiple entries."""

        for entry in entries:
            if not entry.state:
                raise ValueError("Entry state must be set for upsert.")

            if existing_entry := self.get(entry.id_):
                existing_entry.state = entry.state
            else:
                self.entries.append(entry)

        self._update_asset()

    def load(self) -> None:
        """Load the asset from Control Room."""

        data = robocorp.storage.get_json(self.asset_name)

        if not data:
            self.entries = []
            return

        for id_, state_name in data.items():
            state = self.available_states.get_by_name(state_name)
            self.entries.append(TrackingAssetEntry(id_=id_, state=state))

    def _update_asset(self) -> None:
        """Save the asset to Control Room."""

        data = {entry.id_: entry.state.name for entry in self.entries}
        robocorp.storage.set_json(self.asset_name, data)
