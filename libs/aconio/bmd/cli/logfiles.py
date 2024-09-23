"""Interpret BMD log files."""

from __future__ import annotations

import os
import re

from robocorp import log
from datetime import datetime
from dataclasses import dataclass


@dataclass
class BMDLogEntry:
    """An entry within a BMD log file."""

    timestamp: datetime
    username: str
    db_user: str
    computer: str
    pid: str
    sid: str
    message: str

    _line_pattern: re.Pattern = re.compile(
        r"(?P<date>.*) (?P<time>.*) SU:(?P<username>.*) BU:(?P<db_user>.*) "
        r"C:(?P<computer>.*) P:(?P<pid>.*) SI:(?P<sid>.*) S:\d* (?P<message>.*)"
    )
    """Regex pattern to parse a line of a BMD log file."""

    @property
    def age(self) -> int:
        """Return the age of the log entry in seconds."""
        time_diff = datetime.now() - self.timestamp
        return time_diff.total_seconds()

    @classmethod
    def from_string(cls, line: str) -> BMDLogEntry:
        """Init a `BMDLogEntry` object from a string.

        Args:
            line:
                The logfile line string to be intrepreted.
        """

        if match := cls._line_pattern.search(line.strip()):
            groups = match.groupdict()  # Extract capture groups

            timestamp = datetime.strptime(
                f'{groups["date"]} {groups["time"]}',
                "%d.%m.%Y %H:%M:%S,%f",
            )

            return BMDLogEntry(
                timestamp=timestamp,
                username=groups["username"],
                db_user=groups["db_user"],
                computer=groups["computer"],
                pid=groups["pid"],
                sid=groups["sid"],
                message=groups["message"],
            )

        else:
            raise ValueError(
                "Regex mismatch: Cannot init BMDLogEntry object from "
                f"string: {line}"
            )


class BMDLogfile:
    """A BMD log file.

    Each BMD log file is responsible for holding log entries of a certain
    topic. For example, the `STDCSVIMPORT.LOG` file holds log entries of
    actions related to the BMD "Standard CSV Import".

    An overview of all BMD log files can be found in the 'Detailliste' section
    within the 'Logdateien' BMD window.
    """

    entries: list[BMDLogEntry]
    """
    List of BMD log file entries (in reverse order, so the most recent entry
    is first in the list).
    """

    def __init__(self, entries: list[BMDLogEntry]) -> None:
        self.entries = entries

    def check_success(
        self,
        success_pattern: str = r"Es wurden \d* von \d* Zeilen .* importiert\.",
        failure_pattern: str = r"Die Daten konnten nicht importiert werden!.*",
        max_entries: int | None = 30,
        max_message_age: int | None = 300,
    ) -> bool:
        """Check if the last logged operation was a success.

        The `success_msg_pattern` and `failure_msg_pattern` variables determine
        the Regex patterns for identifying success or failure messages in the
        logfile.

        The entries of the lofile will be traversed in reverse order (so the
        most recent entry is checked first). If the `message` part of the entry
        matches the `success_msg_pattern`, the last operation is considered to
        be a success and the function returns `True`. Respectively, if the
        message matches the `failure_pattern`, the function returns `False`.

        If `max_entries` is reached, or all of the log file's entries have been
        inspected and none matche the success, nor the failure criteria, an
        error is raised. Setting `max_entries` to `None` will cause the
        function to always inspect the entire log file.

        Only log entries not older than the amount of seconds specified with
        `max_message_age` will be inspected. If none of the log messages within
        that timeframe match the success, nor the failure critera, an error is
        raised. Setting `max_message_age` to `None` will disable this check.

        Only log entries where the `username` column matches the currently
        logged in Windows user will be traversed. The currently logged in user
        is obtained through the `USERNAME` environment variable. The prevents
        the function from finding false-positives through operations of other
        users, since BMD always logs operations of all users into the same
        file.

        Args:
            success_pattern:
                Regex pattern for identifying a success message. Defaults to
                `Es wurden \\d* von \\d* Zeilen .* importiert\\.`
            failure_pattern:
                Regex pattern for identifying a failure message. Defaults to
                `Die Daten konnten nicht importiert werden!.*`
            max_entries:
                Maximum amount of log file entries to traverse. If `None`, all
                entries will be inspected. Defaults to `None`.
            max_message_age:
                Maximum age of the checked log messages in seconds.
                Defaults to `None`.

        Returns:
            Boolean indicating if the operation was successful.
        """

        user = os.environ.get("USERNAME")

        entry_cnt = 0
        for entry in self.entries:
            if max_message_age:
                if entry.age > max_message_age:
                    raise RuntimeError(
                        "Log messages in the given timeframe did not match "
                        "the success, nor the failure criteria!"
                    )

            if entry.username != user:
                continue

            if re.match(success_pattern, entry.message):
                return True
            elif re.match(failure_pattern, entry.message):
                return False
            else:
                entry_cnt += 1
                if entry_cnt >= max_entries:
                    raise RuntimeError(
                        "Max entries reached. Log messages did not match the "
                        "success, nor the failure criteria!"
                    )

    @classmethod
    def from_file(cls, file: str, max_lines: int = 30) -> BMDLogfile:
        """Init a `BMDLogfile` object from a BMD log file.

        Args:
            file:
                Full path to the BMD log file.
            max_lines:
                Maximum amount of lines to read from the log file.
                Defaults to 30.
        """

        entries = []
        line_cnt = 0
        for line in reverse_readlines(file):
            if line_cnt >= max_lines:
                break

            try:
                entries.append(BMDLogEntry.from_string(line))
            except ValueError:
                log.warn(
                    f"Failed to parse log line: '{line}'! "
                    "Skipping this line for logfile reading."
                )

            line_cnt += 1

        return BMDLogfile(entries)


def reverse_readlines(file: str):
    """Return a generator yielding each line of the given file in reverse order.

    Args:
        file:
            Full path to the file which should be read.
    """
    with open(file, "rb") as file:
        file.seek(0, os.SEEK_END)  # Move to EOF
        position = file.tell()
        line = b""
        while position >= 0:
            file.seek(position)
            char = file.read(1)
            if char == b"\n" or char == b"\r":
                if line:
                    yield line[::-1].decode("utf-8", errors="replace")
                line = b""
            else:
                line += char
            position -= 1
        if line:
            yield line[::-1].decode("utf-8", errors="replace")
