"""Aconio wrapper for clipboard operations."""

import pathlib
import pyperclip
import subprocess


def clear_clipboard() -> None:
    """Clear the clipboard."""

    pyperclip.copy("")


def get_clipboard() -> str | None:
    """Get the current clipboard content as a string."""

    content = pyperclip.paste()
    return content if content else None


def set_clipboard(value: str) -> None:
    """Set the clipboard."""

    pyperclip.copy(value)


def set_file_to_clipboard(file_path: pathlib.Path) -> None:
    """Set the clipboard to the content of a file.

    Uses PowerShell to set the clipboard to the file. This is useful for
    uploading files via copy-paste operations in Windows applications.

    Only works on Windows.
    """

    # Sanitize the file path for PowerShell command. This is
    # so we can later pass the path enclosed in double quotes
    # to avoid issues with spaces in paths.
    sanitized_filepath = str(file_path).replace('"', '""')

    cmd = [
        "powershell",
        "Set-Clipboard",
        "-LiteralPath",
        f'"{sanitized_filepath}"',
    ]
    subprocess.run(cmd, check=True)
