"""Manage the robot data directory holding configs and temporary files.

Example:
```python
from aconio import botdata

# Create '/my/bot/dir' and robot temp & config directories
botdata.create(name='vz_process', root='/my/bot/dir')

botdata.base_dir()      # '/my/bot/dir/vz_process'
botdata.temp_dir()      # '/my/bot/dir/vz_process/temp'
botdata.config_dir()    # '/my/bot/dir/vz_process/config'

# Load the process configuration form an Azure file share into
# '/my/bot/dir/vz_process/config'
botdata.load_process_config_from_azure(
    storage_dir_path: 'bot_configs/vz_process/some_client', 
    account_url: 'https://robocorpstorage.file.core.windows.net/', 
    share_name: 'robocorp-files',
    access_key: 'MY_ACCESS_KEY',
)

# Some Robot Code...

# Delete all files in '/my/bot/dir/vz_process/temp' which were generated
# during a robot run
botdata.cleanup_temp()
```
"""

import os
import shutil
import tempfile

from aconio import azure
from aconio.core import utils
from aconio.botdata import _config as cfg

from functools import lru_cache


# This module does not expose the configuration to the outside.
@lru_cache  # Always return the same instance.
def _config() -> cfg.Config:
    return cfg.Config()


def create(name: str, root: str = tempfile.gettempdir()) -> None:
    """Create the robot data directory and sub-directories `temp` and `config`.

    If the robot directory already exists, it will be re-created with empty
    `temp` and `config` folders.

    Args:
        name:
            Name of the created robot data directory.
        root:
            The root directory where `name` and the respective `temp` and
            `config` directories will be created.
            Defaults to `tempfile.gettempdir()`.
        create_root:
            Determines if the root path of the robot dir specified through
            `aconio.botdata.configure()` should also be created.
    """
    root = os.path.realpath(root)

    _config().base_dir = os.path.join(root, name)

    if os.path.exists(_config().base_dir):
        shutil.rmtree(_config().base_dir)

    # This also automatically creates the base_dir
    os.makedirs(_config().temp_dir, exist_ok=True)
    os.makedirs(_config().config_dir, exist_ok=True)


def base_dir() -> str:
    """Get the robot data base directory.

    Returns:
        The path to the robot data base directory containing the `temp` &
        `config` directories.

    Raises:
        RuntimeError: If the configured path for the base directory does not
        exist.
    """
    _check_base_dir()
    return _config().base_dir


def temp_dir() -> str:
    """Get the robot `temp` directory.

    Returns:
        The path to the robot `temp` directory.

    Raises:
        RuntimeError: If the `temp` directory does not exist.
    """
    _check_base_dir()
    if not os.path.exists(_config().temp_dir):
        raise RuntimeError(
            f"Directory {_config().temp_dir} does not exist. "
            "Did you call create()?"
        )

    return _config().temp_dir


def config_dir() -> str:
    """Get the robot `config` directory.

    Returns:
        The path to the robot `config` directory.

    Raises:
        RuntimeError: If the `config` directory does not exist.
    """
    _check_base_dir()
    if not os.path.exists(_config().config_dir):
        raise RuntimeError(
            f"Directory {_config().config_dir} does not exist. "
            "Did you call create()?"
        )

    return _config().config_dir


def load_process_config_from_azure(
    storage_dir_path: str, account_url: str, share_name: str, access_key: str
) -> None:
    """Load process configuration from Azure file share into `config` folder.

    Always overwrites a pre-existing configuration.

    Args:
        storage_dir_path:
            Path to the config directory in the Azure file share.

        account_url:
            URL of the Azure storage account.

        share_name:
            Name of the Azure file share.

        access_key:
            Azure storage account access key.
    """
    # Use 'config_dir()', which throws an error if the user hasn't already
    # created the robot data directory with 'create()'
    shutil.rmtree(config_dir())

    # Use 'config_dir' from 'config()' to avoid the error because the directory
    # does not exist
    os.mkdir(_config().config_dir)

    azure.download_storage_dir(
        storage_dir_path=storage_dir_path,
        output_path=config_dir(),
        auth=azure.Auth(
            account_url=account_url,
            share_name=share_name,
            credential=access_key,
        ),
    )


def cleanup_temp() -> None:
    """Remove all files in the temporary robot directory."""
    utils.cleanup_folder(temp_dir=temp_dir())


def _check_base_dir():
    if not _config().base_dir or not os.path.exists(_config().base_dir):
        raise RuntimeError(
            f"Directory {_config().base_dir} does not exist. "
            "Did you call create()?"
        )
