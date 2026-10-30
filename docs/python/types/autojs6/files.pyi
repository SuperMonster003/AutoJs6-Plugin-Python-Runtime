# Type stub of the AutoJs6 Python Runtime package `autojs6` (mirrors app/src/main/python/autojs6/files.py).
# AutoJs6 tools/api-coverage/language_runtimes.py checks its names and signatures against the plugin.
"""Bounded live access to the current script's Host-side directory."""

import builtins
import os
from typing import Final

MAX_LIST_ENTRIES: Final[int]
MAX_PATH_BYTES: Final[int]
MAX_TEXT_BYTES: Final[int]


def exists(path: str | os.PathLike[str]) -> bool:
    """Return whether one safe path currently exists in the Host execution root."""
    ...


def is_dir(path: str | os.PathLike[str]) -> bool:
    """Return whether one safe path is currently a Host-side directory."""
    ...


def is_file(path: str | os.PathLike[str]) -> bool:
    """Return whether one safe path is currently a regular Host-side file."""
    ...


def list(path: str | os.PathLike[str] = ...) -> builtins.list[str]:
    """List at most 128 sorted direct child names from one Host-side directory."""
    ...


def read_text(path: str | os.PathLike[str], *, encoding: str = ...) -> str:
    """Read one bounded UTF-8 file from the live Host execution root."""
    ...


def write_text(path: str | os.PathLike[str], text: str, *, encoding: str = ...) -> None:
    """Overwrite one file in the live Host execution root without creating parents."""
    ...
