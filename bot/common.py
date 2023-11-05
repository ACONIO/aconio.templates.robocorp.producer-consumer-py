"""This file contains shared functions used by multiple tasks."""

import os
import shutil

from robocorp import log


def cleanup_robot_tmp_folder(temp_dir: str):
    """Removes all documents from the robot temp folder to cleanup previous runs."""
    for file_name in os.listdir(temp_dir):
        file = os.path.join(temp_dir, file_name)
        try:
            if os.path.isfile(file) or os.path.islink(file):
                log.debug(f'removing file {file}')
                os.remove(file)
            elif os.path.isdir(file):
                log.debug(f'removing directory {file}')
                shutil.rmtree(file)
        except Exception as e:
            log.warn(f'failed to delete {file}. reason: {e}')
