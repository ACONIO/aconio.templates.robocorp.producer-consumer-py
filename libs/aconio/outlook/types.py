"""Outlook-specific types."""

import enum


class FolderType(enum.Enum):
    """Outlook folder types mapped to their respective IDs."""

    INBOX = 6
    OUTBOX = 4
    SENT = 5
    DELETED = 3
    DRAFTS = 16
    JUNK = 23
    CALENDAR = 9
    CONTACTS = 10
    TASKS = 13
