# Type stub of the AutoJs6 Python Runtime package `autojs6` (mirrors app/src/main/python/autojs6/project.py).
# AutoJs6 tools/api-coverage/language_runtimes.py checks its names and signatures against the plugin.
"""Bounded read-only convenience access to the private project snapshot."""

import os
from typing import Final

MAX_READ_BYTES: Final[int]


def exists(path: str | os.PathLike[str]) -> bool:
    """Return whether a safe project-relative path names a regular file."""
    ...


def read_bytes(path: str | os.PathLike[str]) -> bytes:
    """Read at most 1 MiB from one regular file in the frozen project workspace."""
    ...


def read_text(path: str | os.PathLike[str], *, encoding: str = ...) -> str:
    """Read one UTF-8 project file with strict decoding and the same 1 MiB limit."""
    ...
