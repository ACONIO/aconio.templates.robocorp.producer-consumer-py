import os
import shutil

from robocorp import log


def cleanup_folder(path: str):
    """Remove all content from the given folder.

    Args:
        path (`str`): The path to the folder to be cleaned up.
    """
    for file_name in os.listdir(path):
        file = os.path.join(path, file_name)
        try:
            if os.path.isfile(file) or os.path.islink(file):
                log.debug(f"removing file {file}")
                os.remove(file)
            elif os.path.isdir(file):
                log.debug(f"removing directory {file}")
                shutil.rmtree(file)
        except Exception as e:
            log.warn(f"failed to delete {file}. reason: {e}")


def currency_to_float(c: str) -> float:
    return float(c.replace(".", "").replace(",", "."))
