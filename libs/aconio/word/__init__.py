"""Wrapper library for Robocorp's `RPA.Word.Application`."""

import functools

from typing import Any

from RPA.Word.Application import Application as WordApp


@functools.lru_cache
def app() -> WordApp:
    return WordApp(autoexit=False)


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
    for paragraph in app()._active_document.Paragraphs:
        if placeholder in paragraph.Range.Text:
            _replace_text_with_image_in_range(
                paragraph.Range, placeholder, image_path
            )


def _replace_text_with_image_in_range(
    doc_range: Any, placeholder: str, image_path: str
) -> None:
    """Replace `placeholder` with image from `image_path` in given `doc_range`.

    Args:
        placeholder:
            The string within the current Word document to be replaced by the
            given image.
        image_path:
            Full path to the image file.
        doc_range:
            The range within the current Word document where the replacement
            should take place.

    Raises:
        ValueError: If the `placeholder` is not found in the given `doc_range`.
    """

    pos = doc_range.Text.find(placeholder)

    if pos == -1:
        raise ValueError(f"Placeholder '{placeholder}' not found in range.")

    # Create a new range specifically for the placeholder
    placeholder_range = doc_range.Duplicate
    placeholder_range.Start = placeholder_range.Start + pos
    placeholder_range.End = placeholder_range.Start + len(placeholder)

    # Clear the placeholder text and insert the image
    placeholder_range.Text = ""
    placeholder_range.InlineShapes.AddPicture(
        FileName=image_path, LinkToFile=False, SaveWithDocument=True
    )
