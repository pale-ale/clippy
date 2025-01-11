"""Copies things to the clipboard, supporting multiple target applications.

This package can be used to copy files, contents, folders etc. to the clipboard.
The excact format can be specified in order to support different applications like
file browsers, web browsers, messengers, and others.
"""

import logging
from collections.abc import Iterable

import click

from clippy.clipsources.clipsource import ClipSource
from clippy.translator import Translator

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("default")


def main_cli() -> None:
    """Entry point for cli use."""
    logger.info("Running cli.")
    t = Translator()
    cmd = t.make_click_command()

    @click.MultiCommand.result_callback(cmd)
    def _callback(*sources: list[ClipSource]) -> None:
        _dispatch(sources=sources[0], translator=t)

    cmd()


def main_gui() -> None:
    """[Unimplemented] Entry point for gui use ."""
    logger.info("Running gui.")


def _dispatch(sources: Iterable[ClipSource], translator: Translator) -> None:
    """Run a configuration."""
    logger.info("Dispatched.")
    if translator.accessor_type is not None:
        accessor = translator.accessor_type(sources)
        accessor.show()
        accessor.write_to_clipboard()
