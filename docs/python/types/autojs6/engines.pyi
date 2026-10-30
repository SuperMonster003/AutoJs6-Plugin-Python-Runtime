# Type stub of the AutoJs6 Python Runtime package `autojs6` (mirrors app/src/main/python/autojs6/engines.py).
# AutoJs6 tools/api-coverage/language_runtimes.py checks its names, signatures and constant values against the plugin.
"""Bounded control over the current Host engine and scoped child scripts."""

import os
from typing import Final, NoReturn

INFO_SCHEMA: Final = "autojs6-python-engine-info-v1"
LAUNCH_SCHEMA: Final = "autojs6-python-engine-launch-v1"
MAX_ENGINE_NAME_BYTES: Final = 256
MAX_SCRIPT_LAUNCHES: Final = 16
MAX_SOURCE_NAME_BYTES: Final = 1024


def current() -> dict[str, object]:
    """Return detached, path-safe metadata for the current Host Python engine."""
    ...


def run(path: str | os.PathLike[str]) -> dict[str, object]:
    """Asynchronously start one scoped non-Python Host script and return its handle."""
    ...


def stop_self() -> NoReturn:
    """Ask the Host to force-stop this engine; this call does not return normally."""
    ...
