"""Provides the FileClipSource class."""

import typing
from collections.abc import Iterable

import click

from clippy.clipboard import ClipboardTarget
from clippy.clipsources.clipsource import ClipSource


class FileClipSource(ClipSource):
    """Provides file paths and their contents to be used for the clipboard selection."""

    __supported_targets: typing.ClassVar = [
        ClipboardTarget.TIMESTAMP,
        ClipboardTarget.URI_LIST,
        ClipboardTarget.GNOME_COPIED_FILES,
    ]

    def __init__(self, files: Iterable[str], targets: Iterable[ClipboardTarget]) -> None:
        """Set up the list of files and build the according target information."""
        super().__init__()
        self.files = files
        self.requested_targets = list(targets)

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

    @staticmethod
    def get_click_subcommand(cmd_name: str) -> click.Command:
        """Return the subcommand with required options etc. to configure this source."""

        def build_source(path: str, **kwargs: bool) -> FileClipSource:
            keys = (k for k, v in kwargs.items() if v)
            return FileClipSource([path], ClipSource.strs_to_targets(keys))

        params = [click.Option(["--path"], required=True, type=click.Path())]
        flags = [
            click.Option(
                ["--" + target.name, "--" + target.name, target.name],
                is_flag=True,
                help="Write to clipboard target " + target.name,
            )
            for target in FileClipSource.__supported_targets
        ]
        params.extend(flags)
        return click.Command(cmd_name, callback=build_source, params=params)
