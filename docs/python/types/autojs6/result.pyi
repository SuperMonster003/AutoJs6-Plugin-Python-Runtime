# Type stub of the AutoJs6 Python Runtime package `autojs6` (mirrors app/src/main/python/autojs6/result.py).
# AutoJs6 tools/api-coverage/language_runtimes.py checks its names and signatures against the plugin.
"""Explicit, bounded structured result for one Python execution."""

from typing import Any


def set(value: Any) -> None:
    """Set exactly one strict JSON-compatible result, independently of stdout."""
    ...
