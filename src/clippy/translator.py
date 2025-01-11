"""Provides the translator class."""

from typing import TYPE_CHECKING

import click

from clippy.clipsources.fileclipsource import FileClipSource

if TYPE_CHECKING:
    from clippy.accessors.accessor import Accessor
    from clippy.clipsources.clipsource import ClipSource

USE_X11 = True


class Translator:
    """Convert command line calls into accessor-source structure.

    This class uses click to parse command line inputs.
    The options are then forwarded to different runtime-generated source and
    accessor objects, which in turn fill the clipboard with requested values.
    """

    def __init__(self) -> None:
        """Configure available types of sources and accessors."""
        self._available_source_types: dict[str, type[ClipSource]] = {
            "file": FileClipSource,
        }
        self.accessor_type: type[Accessor] | None = None
        if USE_X11:
            from clippy.accessors.x11accessor import X11Accessor

            self.accessor_type = X11Accessor

    def make_click_command(self) -> click.Command:
        """Build the click.Command from various sources."""
        cmds = []
        for src_name, src_type in self._available_source_types.items():
            cmds.append(src_type.get_click_subcommand(src_name))
        return click.Group("group1", cmds, chain=True)
