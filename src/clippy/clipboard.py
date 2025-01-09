"""Contains the ClipboardTarget enum."""

import enum


class ClipboardTarget(enum.Enum):
    """Holds different contenttypes."""

    PLAINTEXT = 0
    FORMATTED_TEXT = 1
    TIMESTAMP = 2
    URI_LIST = 3
    GNOME_COPIED_FILES = 4
