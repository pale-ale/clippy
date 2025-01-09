"""Copies things to the clipboard, supporting multiple target applications.

This package can be used to copy files, contents, folders etc. to the clipboard.
The excact format can be specified in order to support different applications like
file browsers, web browsers, messengers, and others.
"""

from .main import main_cli, main_gui

__all__ = ["main_cli", "main_gui"]
