"""Utility functions for `aconio.bmd.cli` modules."""

import os
import glob

from aconio.bmd._config import config


def create_import_file(filename: str) -> str:
    """Create a temporary file for BMD imports.

    The import file will be created with the given `filename` in the temp
    directory passed via the module configuration.

    Perform the following validations:
    - Check if the `temp_path` was set via module config
    - Cleanup any leftover import files from possible previous runs

    Args:
        filename:
            Name of the file to be created. File extension must be provided
            as well.

    Returns:
        The absolute filepath of the created file.
    """
    if not config().temp_path:
        raise ValueError(
            f"Failed to determine temp dir for storing '{filename}'. "
            "Did you set the module configuration?"
        )

    # Cleanup previous import files (BMD renames the file after the import
    # and adds the date to the filename, which is why the * is needed here)
    name = filename.split(".")[0]
    extension = filename.split(".")[1]
    prev_files = glob.glob(
        os.path.join(config().temp_path, f"{name}*.{extension}")
    )
    for prev_file in prev_files:
        os.remove(prev_file)

    return os.path.abspath(os.path.join(config().temp_path, filename))
