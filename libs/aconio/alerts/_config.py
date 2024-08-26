"""Manage global module configuration."""

import jinja2 as j2

from enum import Enum
from typing import List


class Config:
    """Global configurations available in `aconio.alerts`."""

    _jinja_env: j2.Environment = None
    _alert_file: str = None
    _alert_types: Enum = None

    @property
    def alert_file(self):
        if self._alert_file:
            return self._alert_file
        else:
            raise ValueError("Config value 'alert_file' is missing.")

    @alert_file.setter
    def alert_file(self, value: str):
        self._alert_file = value

    @property
    def jinja_env(self):
        if self._jinja_env:
            return self._jinja_env
        else:
            raise ValueError("Config value 'jinja_template_path' is missing.")

    @jinja_env.setter
    def jinja_env(self, value: str):
        self._jinja_env = value

    @property
    def alert_types(self):
        if self._alert_types:
            return self._alert_types
        else:
            raise ValueError("Config value 'alert_types' is missing.")

    @alert_types.setter
    def alert_types(self, value: List[str]):
        """Convert given list to enum before setting `alert_types`."""
        self._alert_types = Enum("AlertType", [v.upper() for v in value])
