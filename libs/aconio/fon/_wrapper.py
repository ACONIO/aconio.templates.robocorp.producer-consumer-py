"""Holds base class for FinanzOnline pseudo-APIs."""

from aconio.fon._auth import FonSession


class _FinanzOnlineWrapperAPI:
    """Base class for FinanzOnline pseudo-APIs."""

    def __init__(self, session: FonSession) -> None:
        self._session = session
