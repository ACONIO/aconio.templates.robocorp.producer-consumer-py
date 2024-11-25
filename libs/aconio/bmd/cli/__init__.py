"""Interact with BMD using the CLI."""

from __future__ import annotations

import os
import functools
import subprocess

from robocorp import log

from aconio.bmd import _params
from aconio.bmd._params import BMDParam
from aconio.bmd._config import config, ExecutableType, BMDLoginDetails


@functools.lru_cache
def ntcs_cli() -> BMDExecutable:
    return BMDExecutable(
        ntcs_dir=config().ntcs_dir,
        exec_type=config().ntcs_exec_type,
        login_details=config().login_params,
    )


class BMDExecutable:
    """Represent a BMD executable."""

    _ntcs_dir: str
    """Path to the BMD directory."""

    _exec_type: ExecutableType
    """BMD executable type."""

    _login_details: BMDLoginDetails | None
    """BMD login information."""

    def __init__(
        self,
        ntcs_dir: str,
        exec_type: ExecutableType,
        login_details: BMDLoginDetails | None = None,
    ) -> None:
        if ntcs_dir:
            self._ntcs_dir = ntcs_dir
        else:
            raise ValueError(
                "'ntcs_dir' is required to determine correct BMD executable! "
                "Did you set the module configuration?"
            )

        if exec_type:
            self._exec_type = exec_type
        else:
            raise ValueError(
                "'exec_type' is required to determine correct BMD executable! "
                "Did you set the module configuration?"
            )

        self._login_details = login_details

    @property
    def executable_path(self) -> str:
        """Full path to the BMD executable."""
        return os.path.join(self._ntcs_dir, self._exec_type.value)

    def start(
        self,
        params: dict[str, str] | None = None,
    ) -> None:
        """Start the configured BMD '.exe' file.

        Args:
            params:
                Additional parameters for the CLI call.
        """
        if params:
            params = _params.bmd_params_from_dict(params)

        self._run(params=params)

    def run_macro(
        self, macro_id: str, params: dict[str, str] | None = None
    ) -> None:
        """Execute a BMD macro via the CLI.

        Args:
            macro_id:
                The `FOR_FORMELNR` of the BMD macro. Can be found in BMD under
                `[TOOLS - Makros]` in the `Formel/Makro-Nr` column.
            params:
                Additional parameters for the CLI call.
        """

        if params:
            params["FOR_FORMELNR"] = macro_id
        else:
            params = {"FOR_FORMELNR": macro_id}

        self.run_function(
            function_name="MCS_MACRO_EXECUTE",
            params=params,
        )

    def run_function(
        self,
        function_name: str,
        params: dict[str, str] = None,
        messages: bool = True,
    ) -> None:
        """Execute a BMD function with the configured BMD executable.

        Note: When using executable type `EXEC`, a BMD window must be visible
        on screen (started via "BMDExec.exe"). Also, possible pop-ups appearing
        after the CLI call must be handeled by the user!

        Args:
            function_name:
                Name of the BMD function to be executed.
            params:
                Additional parameters for the CLI call.
            messages:
                If false, `/NOMESSAGES=1` will be passed to the CLI call, which
                prevents any pop-ups from showing up after the import. Defaults
                to `True`.
        """

        bmd_parameters = [
            BMDParam("PRODUCT", "BMDNTCS"),
            BMDParam("FUNC", function_name),
        ]

        if params:
            bmd_parameters.extend(_params.bmd_params_from_dict(params))

        if messages:
            bmd_parameters.append(BMDParam("NOMESSAGES", "0"))
        else:
            bmd_parameters.append(BMDParam("NOMESSAGES", "1"))

        # If exec type `NTCS` is used, a new BMDNTCS instance is created
        # for every command. Thus, pass the '/FINISH' parameter to
        # immediately close the instance after the command has finished.
        if self._exec_type == ExecutableType.NTCS:
            bmd_parameters.append(BMDParam("FINISH"))

        self._run(bmd_parameters)

    def _run(self, params: list[BMDParam]) -> None:
        """Run a command against the BMD executable.

        If login details have been set, they will be added implicitly.
        """

        if not params:
            params = []

        # Add custom BMD login parameters
        if self._login_details:
            params.extend(self._login_details.get_params())

        cmd = [self.executable_path]
        cmd.extend([str(p) for p in params])

        log.info(f"Running BMD CLI command: {cmd}")
        subprocess.run(cmd, check=True)
