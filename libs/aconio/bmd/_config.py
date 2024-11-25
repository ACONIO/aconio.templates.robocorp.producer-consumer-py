"""Manage global module configuration."""

from __future__ import annotations

import os
import functools
import dataclasses

from aconio.bmd._exec_types import ExecutableType
from aconio.bmd._params import BMDParam


@functools.lru_cache
def config() -> Config:
    return Config()


@dataclasses.dataclass
class Config:
    """Global configurations available in `aconio.bmd`."""

    temp_path: str | None = None
    """
    Path to a temporary directory for storing generated files.
    """

    ntcs_dir: str = os.environ.get("BMDNTCSDIR")
    """NTCS directory holding 'BMDNTCS.exe' and 'BMDExec.exe'."""

    bmd_locator: str = 'subname:"BMD - Software"'
    """The `robocorp.windows` locator to identify the main BMD window."""

    _ntcs_exec_type: ExecutableType | None = None
    """
    Determine if the BMDExec or BMDNTCS executable will be used for running
    CLI commands.
    """

    _ntcs_log_dir: str | None = None
    """
    Path to the BMD LOG directory.
    
    Only required if the environment is missing the `BMDKDNR` or `NTCSVersion`
    environment variables, otherwise the path will be constructed using these
    env vars.
    """

    login_params: BMDLoginDetails | None = None
    """Details for a custom BMD login."""

    @property
    def log_dir(self) -> str:
        if not self._ntcs_log_dir:
            return _get_log_dir()
        else:
            return self._ntcs_log_dir

    @log_dir.setter
    def log_dir(self, value: str) -> None:
        self._ntcs_log_dir = value

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
                "Please use 'ExecutableType' or 'str'."
            )

    def set_login_details(self, db: str, username: str, password: str) -> None:
        """Set BMD login details."""

        self.login_params = BMDLoginDetails(
            db=db, username=username, password=password
        )


@dataclasses.dataclass
class BMDLoginDetails:
    """Information required to specify a custom BMD login."""

    db: str
    """Equivalent to `DBALIAS` BMD parameter."""

    username: str
    """Equivalent to `USERID` BMD parameter."""

    password: str
    """Equivalent to `PWD` BMD parameter."""

    def get_params(self) -> list[BMDParam]:
        """Return the login information as BMD CLI parameters."""
        return [
            BMDParam("DBALIAS", self.db),
            BMDParam("USERID", self.username),
            BMDParam("PWD", self.password),
        ]


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
