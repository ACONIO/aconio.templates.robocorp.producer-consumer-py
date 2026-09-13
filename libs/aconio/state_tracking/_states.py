"""Robot run progression states."""

import pydantic


class StateNotFoundError(Exception):
    """Exception when an invalid state is retrieved from a state list."""

    pass


class State(pydantic.BaseModel):
    """A processing state of an entity during a bot run."""

    model_config = pydantic.ConfigDict(frozen=True)

    name: str
    """Name of the state."""

    order: int
    """Processing order of the state."""

    def __lt__(self, other):
        if isinstance(other, State):
            return self.order < other.order
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, State):
            return self.order <= other.order
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, State):
            return self.order > other.order
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, State):
            return self.order >= other.order
        return NotImplemented


class States:
    """A collection of states."""

    def __init__(self, state_dict: dict[str, int]):
        """Initialize the states from a dictionary."""
        self._states = [State(name=k, order=v) for k, v in state_dict.items()]

    @property
    def lowest(self) -> State:
        """
        The state with the lowest order — used as the initial state for
        newly loaded entries.
        """
        return min(self._states, key=lambda s: s.order)

    def get_by_name(self, name: str) -> State:
        """Get a state by its name."""
        if self._states:
            for state in self._states:
                if state.name == name:
                    return state

        raise StateNotFoundError(f"State {name} not found in states list.")
