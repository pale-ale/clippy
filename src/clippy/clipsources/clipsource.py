"""Contains the ClipSource class."""

from collections.abc import Callable, Iterable
from typing import Any

from clippy.clipboard import ClipboardTarget


class ClipSource:
    """ClipSources act as inputs to be inserted into the clipboard."""

    def __init__(self) -> None:
        """Set up the target->value dispatch."""
        self._value_proxy: dict[ClipboardTarget, Callable] = {}

    @property
    def targets(self) -> Iterable[ClipboardTarget]:
        """Fetch all supported targets for this source."""
        return self._value_proxy.keys()

    def get_value(self, target: ClipboardTarget) -> Any:  # noqa: ANN401
        """Get the current value for the target type."""
        return self._value_proxy[target]()
