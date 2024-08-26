"""Manage global module configuration."""

import os


class Config:
    """Global configurations available in `aconio.botdata`."""

    base_dir: str = None

    def __init__(self, path: str = None):
        if path:
            self.base_dir = os.path.join(path, "temp")

    @property
    def config_dir(self) -> str:
        return os.path.join(self.base_dir, "config")

    @property
    def temp_dir(self) -> str:
        return os.path.join(self.base_dir, "temp")
