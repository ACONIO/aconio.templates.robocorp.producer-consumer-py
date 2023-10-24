"""This file contains shared functions used by multiple tasks."""

import os


def cleanup_robot_tmp_folder(temp_dir: str):
    """Removes all documents from the robot temp folder to cleanup previous runs."""
    for file_name in os.listdir(temp_dir):
        file = temp_dir + file_name
        if os.path.isfile(file):
            os.remove(file)
