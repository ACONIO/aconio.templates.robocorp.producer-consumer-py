"""Collection of locators for the `aconio.dvo.ui` module."""

from __future__ import annotations

import os
import functools
import dataclasses


@dataclasses.dataclass
class DVOLocators:
    """Collection of DVO-related locators usable by `RPA.Desktop`."""

    _images_folder: str = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "_images"
    )

    def __init__(self, images_folder: str | None = None) -> None:
        if images_folder:
            self._images_folder = images_folder

    def _image(self, filename: str) -> str:
        """Return a proper image locator specifier for the given filename.

        The full image path is constructued using the specified images folder
        upon class initialization.
        """
        return "image:" + os.path.join(self._images_folder, filename)

    @property
    def clear_filters(self) -> str:
        return self._image("clear_filters.png")

    @property
    def open_attachment(self) -> str:
        return self._image("open_attachment.png")

    @property
    def complete_task(self) -> str:
        return self._image("complete_task.png")


@functools.lru_cache
def locators() -> DVOLocators:
    return DVOLocators()
