"""Test the different accessors."""

import unittest

from clippy.accessors.x11accessor import X11Accessor
from clippy.clipboard import ClipboardTarget
from clippy.clipsources.fileclipsource import FileClipSource


class TestX11Accessor(unittest.TestCase):
    """Contains test cases for the X11 acessor."""

    def test_available_targets_empty(self) -> None:
        """Check that an accessor without sources has no available targets."""
        a = X11Accessor([])
        self.assertEqual(list(a.get_supported_targets()), [])

    def test_available_targets_file(self) -> None:
        """Check that the targets provided by a FileClipSource are recognized."""
        file_path = "test.txt"
        supported_targets = [
            ClipboardTarget.TIMESTAMP,
            ClipboardTarget.URI_LIST,
            ClipboardTarget.GNOME_COPIED_FILES,
        ]
        source = FileClipSource([file_path], supported_targets)
        a = X11Accessor([source])
        self.assertEqual(list(a.get_supported_targets()), supported_targets)
        self.assertEqual(
            source.get_value(ClipboardTarget.URI_LIST),
            f"file://{file_path}",
        )
