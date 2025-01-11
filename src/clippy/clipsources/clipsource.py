"""Contains the ClipSource class."""

from abc import abstractmethod
from collections.abc import Callable, Iterable
from typing import Any

import click

from clippy.clipboard import ClipboardTarget


class ClipSource:
    """ClipSources act as inputs to be inserted into the clipboard."""

    def __init__(self) -> None:
        """Set up the target->value dispatch."""
        self._value_proxy: dict[ClipboardTarget, Callable] = {}
        self.requested_targets: Iterable[ClipboardTarget] = []

    @property
    def supported_targets(self) -> Iterable[ClipboardTarget]:
        """Fetch all supported targets for this source."""
        return self._value_proxy.keys()

    def get_value(self, target: ClipboardTarget) -> Any:  # noqa: ANN401
        """Get the current value for the target type."""
        return self._value_proxy[target]()

    @staticmethod
    @abstractmethod
    def get_click_subcommand(cmd_name: str) -> click.Command:
        """Return the subcommand with required options etc. to configure this source."""

    @staticmethod
    def strs_to_targets(strs: Iterable[str]) -> Iterable[ClipboardTarget]:
        """Lookup the provided name and return the according target enum."""
        for s in strs:
            t = ClipboardTarget._member_map_.get(s, None)
            if t is not None:
                assert isinstance(t, ClipboardTarget)  # noqa: S101
                yield t
