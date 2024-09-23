"""This module contains utility functions."""

import os
import time
import shutil
import base64
import locale

from typing import Callable, Any
from urllib.parse import quote


def filter_none_and_join(lst: list, sep: str = " ") -> str:
    """Filter `lst` for `None` and join with `sep`."""
    return sep.join(filter(None, lst))


def cleanup_folder(temp_dir: str) -> None:
    """Remove all content from the given folder."""

    for file_name in os.listdir(temp_dir):
        file = os.path.join(temp_dir, file_name)

        if os.path.isfile(file) or os.path.islink(file):
            os.remove(file)
        elif os.path.isdir(file):
            shutil.rmtree(file)


def url_encode(url_to_encode: str):
    """URL-encodes the given string.

    Args:
        url_to_encode: String to encode.

    Returns:
        Encoded string.
    """
    return quote(url_to_encode)


def b64_encode_image(path_to_file: str) -> bytes:
    """Base64 encode the given image file and return a bytes object.

    Useful e.g. for embedding images into an Outlook E-Mail body using
    `<img src="data:image/jpg;base64,<b64_encoded_image>">`.

    Note that for the above html code to work, you first need to decode the
    return value of this function to UTF-8: `b64_encoded_image.decode("utf-8")`
    before passing it to the HTML.

    Args:
        path_to_file: Path to the file which should be base64 encoded.

    Returns:
        Base64 encoded file.
    """
    with open(path_to_file, "rb") as file:
        return base64.b64encode(file.read())


def from_german_currency_string(c: str) -> float:
    """Parse currency string to float."""
    return float(c.replace(".", "").replace(",", "."))


def to_german_currency_string(number: float, show_currency_symbol: bool) -> str:
    """Return string representation of a float in German currency formatting.

    German currency formatting means that a dot is used as thousand separation
    and comma as decimal seperation.

    Example: `1_000_000.50` -> `"1.000.000,50"`

    Args:
        number: Float to format.

        show_currency_symbol:
            If True, append "€" at the end of the string.

    Returns:
        Formatted number as string.
    """
    try:
        locale.setlocale(locale.LC_MONETARY, "de_DE.UTF-8")
    except locale.Error:
        locale.setlocale(locale.LC_MONETARY, "German_Austria.1252")

    return locale.currency(number, symbol=show_currency_symbol, grouping=True)


def replace_template_values(template_file: str, replace_values: dict[str, str]):
    """Replace placeholders with given values in a template `.txt` file.

    Args:
        template_file:
            Path to the `.txt` template file containing the according
            placeholders.

        replace_values:
            Dictionary where a key is a specific placeholder in the given
            template file (e.g. `${first_name}`) and the value is the value
            this placeholder should be replaced with (e.g. "Max").

    Returns:
        Content of template file with all given placeholders replaced.
    """
    with open(file=template_file, encoding="utf-8") as template_file:
        output_file = template_file.read()

    # For each entry in dict, perform replace in file
    for placeholder, replace_value in replace_values.items():
        output_file = output_file.replace(placeholder, replace_value)

    return output_file


def wait_until_succeeds(
    retries: int, timeout: int, function: Callable[..., Any], *args, **kwargs
) -> Any:
    """Call a function until it succeeds or `retries` is reached.

    Args:
        retries:
            Maximum number of retries.

        timeout:
            Amount of seconds to wait to retry calling the function.

        function:
            Callable to execute.

        *args:
            Positional arguments to pass to `function`.

        **kwargs:
            Keyword arguments to pass to `function`.

    Returns:
        The return value of the given `function`.
    """

    for i in range(retries):
        try:
            res = function(*args, **kwargs)
            break
        except Exception as exc:  # pylint: disable=broad-except
            if i < retries - 1:  # i is zero indexed
                time.sleep(timeout)
            else:
                raise exc
    return res


def wait_until_file_exits(file: str, retries: int, timeout: int = 1) -> None:
    """Wait until a file exists or the maximum number of retries is reached.

    Args:
        file:
            File to wait for.

        retries:
            Amount of retries to open the file.

        timeout:
            Amount of seconds to wait to retry to open the file.
            Defaults to 1.

    Raises:
        `FileNotFoundError`:
            If file still doesn't exist after given period of time.
    """

    cnt = 0
    while not os.path.exists(file):
        time.sleep(timeout)
        cnt += 1
        if cnt > retries:
            raise FileNotFoundError(
                f'File "{file}" not found after waiting for {retries} seconds'
            )


def stringify_obj_attrs(item: object, default: str = "") -> object:
    """Parse attributes of object to string.

    Args:
        item:
            Object to parse.

        default:
            Default value to set if attribute is None.
            Defaults to "".
    """
    for field, val in vars(item).items():
        if val is not None:
            setattr(item, field, str(val))
        else:
            setattr(item, field, default)
    return item
