"""Wrapper library for Robocorp's `RPA.Word.Application`."""

import functools

from RPA.Word.Application import Application as WordApp


@functools.lru_cache
def _word() -> WordApp:
    return WordApp()


def replace_text_with_image(placeholder: str, image_path: str) -> None:
    """Replace `placeholder` with image from `image_path`.

    Args:
        placeholder:
            The string within the current Word document to be replaced by the
            given image.
        image_path:
            Full path to the image file.
    """

    # pylint: disable=protected-access
    for paragraph in _word()._active_document.Paragraphs:
        if placeholder in paragraph.Range.Text:
            _word().replace_text(placeholder, "")
            paragraph.Range.InlineShapes.AddPicture(image_path)
