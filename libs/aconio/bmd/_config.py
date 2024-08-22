"""Manage global module configuration."""

from __future__ import annotations

import os
import enum
import dataclasses
import functools


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


def _get_log_dir() -> str:
    """Obtain the BMD LOG folder through environment variables."""

    bmd_customer_id = os.environ.get("BMDKDNR")
    if not bmd_customer_id:
        raise RuntimeError(
            "Failed to determine BMD log folder. Missing "
            "env var 'BMDKDNR'. Please set 'config().log_dir' manually."
        )

    if bmd_version := os.environ.get("NTCSVersion"):
        bmd_version = bmd_version.lower()
    else:
        raise RuntimeError(
            "Failed to determine BMD log folder. Missing "
            "env var 'NTCSVersion'. Please set 'config().log_dir' manually."
        )

    return os.path.join(
        rf"\\bmdasp02-{bmd_version}",
        "bmdntcs_pgmdata",
        bmd_customer_id,
        "LOG",
    )


@dataclasses.dataclass
class Config:
    """Global configurations available in `aconio.bmd.cli`."""

    temp_path: str | None = None
    """
    Path to the temporary robot directory for storing generated files.
    """

    ntcs_dir: str = os.environ.get("BMDNTCSDIR")
    """Path the the BMDNTCS and BMDExec executables."""

    _log_dir: str | None = None
    """
    Path to the BMD LOG directory.
    
    Only required if the environment is missing the `BMDKDNR` or `NTCSVersion`
    environment variables, otherwise the path will be constructed using these
    env vars.
    """

    _ntcs_exec_type: ExecutableType | None = None
    """
    Determine if the BMDExec or BMDNTCS executable will be used for running
    CLI commands.
    """

    @property
    def log_dir(self) -> str:
        if not self._log_dir:
            return _get_log_dir()
        else:
            return self._log_dir

    @log_dir.setter
    def log_dir(self, value: str) -> None:
        self._log_dir = value

    @property
    def ntcs_exec_type(self) -> ExecutableType:
        return self._ntcs_exec_type

    @ntcs_exec_type.setter
    def ntcs_exec_type(self, value: ExecutableType | str) -> None:
        if isinstance(value, str):
            self._ntcs_exec_type = ExecutableType.from_string(value)
        elif isinstance(value, ExecutableType):
            self._ntcs_exec_type = value
        else:
            raise ValueError(
                f"Cannot parse variable of type {type(value)}. "
                "Please use ExecutableType or str."
            )


@functools.lru_cache
def config() -> Config:
    return Config()
