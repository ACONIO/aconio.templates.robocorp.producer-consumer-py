"""Representation of BMD executable types."""

from __future__ import annotations

import enum


class ExecutableType(enum.StrEnum):
    """Type of BMD executable.

    The 'NTCS' executable type is the default way of interacting with BMD.
    It will start the BMD UI and is intended for normal operations. The
    disadvantage of using this executable type for CLI operations, is that
    every time a CLI command is sent to 'BMDNTCS.exe', a new BMD instance will
    be started and thus a new UI window will open.

    The 'EXEC' executable type is intended mainly for CLI operations, since
    multiple CLI calls can be sent to 'BMDExec.exe' and only one instance of
    the BMD window will remain open.
    """

    NTCS = "BMDNTCS.exe"
    EXEC = "BMDExec.exe"

    @classmethod
    def from_string(cls, value: str) -> ExecutableType:
        """Convert string to `ExecutableType`.

        Args:
            value:
                Must either be 'NTCS' or 'EXEC'.
        """
        match value:
            case "NTCS":
                return ExecutableType.NTCS
            case "EXEC":
                return ExecutableType.EXEC
            case _:
                raise ValueError(
                    f"Invalid BMD executable type '{value}'! "
                    "Please use 'NTCS' or 'EXEC'."
                )
