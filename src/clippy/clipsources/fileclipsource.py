"""Provides the FileClipSource class."""

from collections.abc import Iterable

from clippy.clipboard import ClipboardTarget
from clippy.clipsources.clipsource import ClipSource


class FileClipSource(ClipSource):
    """Provides file paths and their contents to be used for the clipboard selection."""

    def __init__(self, files: Iterable[str]) -> None:
        """Set up the list of files and build the according target information."""
        super().__init__()
        self.files = files

        # uri-list contains each file URI, separated by a newline
        uri_list = ""
        for path in self.files:
            uri_list += f"file://{path}\n"
        uri_list = uri_list.rstrip("\n")

        # needed for gnome to differentiate between copy and cut operations
        gnome_cp_files = f"copy\n{uri_list}" if uri_list else ""

        # set the correct data source for every target type
        self._value_proxy[ClipboardTarget.TIMESTAMP] = lambda: "2025-1-1:10-10-10"
        self._value_proxy[ClipboardTarget.URI_LIST] = lambda: uri_list
        self._value_proxy[ClipboardTarget.GNOME_COPIED_FILES] = lambda: gnome_cp_files
