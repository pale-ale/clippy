"""Copies things to the clipboard, supporting multiple target applications.

This package can be used to copy files, contents, folders etc. to the clipboard.
The excact format can be specified in order to support different applications like
file browsers, web browsers, messengers, and others.
"""

import logging
from collections.abc import Callable, Iterable

import click

from clippy.accessors.x11accessor import X11Accessor
from clippy.clipboard import ClipboardTarget
from clippy.clipsources.fileclipsource import FileClipSource

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("default")


def main_cli() -> None:
    """Entry point for cli use."""
    logger.info("Running cli.")
    build_command(_dispatch, _get_supported_targets())()
    _dispatch()


def main_gui() -> None:
    """[Unimplemented] Entry point for gui use ."""
    logger.info("Running gui.")


def build_command(callback: Callable, target_optnames: Iterable[str]) -> click.Command:
    """Create the click command with all supported targets as flags."""
    params: list[click.Parameter] = [
        click.Option(
            [
                "--" + target_optname,
                "--" + target_optname,
                target_optname,
            ],  # Preserve case
            is_flag=True,
            help="Write to clipboard target " + target_optname,
        )
        for target_optname in target_optnames
    ]
    params.append(click.Option(["--FILE"], show_default=True, type=click.Path()))
    return click.Command(None, callback=callback, params=params)


def _dispatch(*args: str, **kwargs: str) -> None:
    logger.info("Dispatched.\nArgs: %s,\nKwargs: %s", args, kwargs)
    file_path = kwargs.pop("file", None)
    selected_targets: list[ClipboardTarget] = [
        ClipboardTarget._member_map_[k] for (k, v) in kwargs.items() if v
    ]
    logger.info("The following targets were requested: %s", selected_targets)
    sources = []
    if file_path is not None:
        sources.append(FileClipSource([file_path]))
    accessor = X11Accessor(sources)
    accessor.show()
    accessor.write_to_clipboard(selected_targets)


def _get_supported_targets() -> Iterable[str]:
    return ClipboardTarget._member_map_.keys()
