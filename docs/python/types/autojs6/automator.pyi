# Type stub of the AutoJs6 Python Runtime package `autojs6` (mirrors app/src/main/python/autojs6/automator.py).
# AutoJs6 tools/api-coverage/language_runtimes.py checks its names, signatures and constant values against the plugin.
"""Bounded, execution-scoped accessibility actions performed by the AutoJs6 Host."""

from typing import Final

DEFAULT_PRESS_DURATION_MILLIS: Final = 100
DEFAULT_SWIPE_DURATION_MILLIS: Final = 300
MAX_COORDINATE: Final = 1000000
MAX_DURATION_MILLIS: Final = 4000


def back() -> bool:
    """Perform Android's global Back action through Host accessibility."""
    ...


def click(x: int, y: int) -> bool:
    """Tap one non-negative screen coordinate through Host accessibility."""
    ...


def home() -> bool:
    """Perform Android's global Home action through Host accessibility."""
    ...


def long_click(x: int, y: int) -> bool:
    """Long-press one non-negative screen coordinate through Host accessibility."""
    ...


def press(x: int, y: int, duration_ms: int = ...) -> bool:
    """Press one screen coordinate for 1..4000 milliseconds."""
    ...


def swipe(x1: int, y1: int, x2: int, y2: int, duration_ms: int = ...) -> bool:
    """Swipe between two screen coordinates for 1..4000 milliseconds."""
    ...
