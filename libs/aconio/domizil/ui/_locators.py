"""Collection of locators for the `aconio.domizil.ui` module."""

import os
import functools


class DOMIZILLocators:
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
    def local_save(self) -> str:
        return self._image("local_save.png")

    @property
    def green_check_save_button(self) -> str:
        return self._image("green_check_save_button.png")

    @property
    def export_dialog(self) -> str:
        return self._image("export_dialog.png")


@functools.lru_cache
def locators() -> DOMIZILLocators:
    return DOMIZILLocators()
