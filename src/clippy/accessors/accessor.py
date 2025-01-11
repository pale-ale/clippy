"""Accessors are tailored to specific window managers and clipboard subsystems."""

import logging
from abc import ABC, abstractmethod
from collections.abc import Iterable

from clippy.clipboard import ClipboardTarget
from clippy.clipsources.clipsource import ClipSource


class Accessor(ABC):
    """Accessors act as an I/O abstraction for clipboard interaction."""

    _logger = logging.getLogger()

    def __init__(self, sources: Iterable[ClipSource]) -> None:
        """Set up accessor base."""
        super().__init__()
        self._sources = list(sources)

    @abstractmethod
    def get_supported_targets(self) -> Iterable[ClipboardTarget]:
        """Return an iterable with every target supported by the current clipboard."""

    @abstractmethod
    def write_to_clipboard(
        self,
        targets: Iterable[ClipboardTarget] | None = None,
    ) -> None:
        """Fill the clipboard with values from the sources."""

    def show(self) -> None:
        """Output the entire clipboard contents with their content types."""
        sourceinfo = "\nSource information:\n"
        for source in self._sources:
            sourceinfo += f"  {source}:\n    Supported targets:\n"
            for target in source.supported_targets:
                sourceinfo += f"      {target}\n"
                sourceinfo += f"        {source.get_value(target)}\n"
            sourceinfo += f"  Requested targets: {list(source.requested_targets)}"
        self._logger.info(sourceinfo)
