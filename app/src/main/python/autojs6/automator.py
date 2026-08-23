"""Bounded, execution-scoped accessibility actions performed by the AutoJs6 Host."""

from __future__ import annotations

from ._broker import _call, _expect_boolean


MAX_COORDINATE = 1_000_000
MAX_DURATION_MILLIS = 4_000
DEFAULT_PRESS_DURATION_MILLIS = 100
DEFAULT_SWIPE_DURATION_MILLIS = 300


def click(x: int, y: int) -> bool:
    """Tap one non-negative screen coordinate through Host accessibility."""
    return _point_action("automator.click", x, y)


def long_click(x: int, y: int) -> bool:
    """Long-press one non-negative screen coordinate through Host accessibility."""
    return _point_action("automator.long_click", x, y)


def press(
    x: int,
    y: int,
    duration_ms: int = DEFAULT_PRESS_DURATION_MILLIS,
) -> bool:
    """Press one screen coordinate for 1..4000 milliseconds."""
    x_value = _coordinate(x, "Press x")
    y_value = _coordinate(y, "Press y")
    duration = _duration(duration_ms, "Press duration")
    return _expect_boolean(
        _call(
            "automator.press",
            {"x": x_value, "y": y_value, "durationMillis": duration},
        ),
        "automator.press",
    )


def swipe(
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    duration_ms: int = DEFAULT_SWIPE_DURATION_MILLIS,
) -> bool:
    """Swipe between two screen coordinates for 1..4000 milliseconds."""
    arguments = {
        "x1": _coordinate(x1, "Swipe x1"),
        "y1": _coordinate(y1, "Swipe y1"),
        "x2": _coordinate(x2, "Swipe x2"),
        "y2": _coordinate(y2, "Swipe y2"),
        "durationMillis": _duration(duration_ms, "Swipe duration"),
    }
    return _expect_boolean(
        _call("automator.swipe", arguments),
        "automator.swipe",
    )


def back() -> bool:
    """Perform Android's global Back action through Host accessibility."""
    return _expect_boolean(_call("automator.back", {}), "automator.back")


def home() -> bool:
    """Perform Android's global Home action through Host accessibility."""
    return _expect_boolean(_call("automator.home", {}), "automator.home")


def _point_action(capability: str, x: int, y: int) -> bool:
    value = _call(
        capability,
        {"x": _coordinate(x, "Action x"), "y": _coordinate(y, "Action y")},
    )
    return _expect_boolean(value, capability)


def _coordinate(value: int, label: str) -> int:
    if type(value) is not int:
        raise TypeError(f"{label} must be an integer")
    if not 0 <= value <= MAX_COORDINATE:
        raise ValueError(f"{label} must be between 0 and {MAX_COORDINATE}")
    return value


def _duration(value: int, label: str) -> int:
    if type(value) is not int:
        raise TypeError(f"{label} must be an integer")
    if not 1 <= value <= MAX_DURATION_MILLIS:
        raise ValueError(f"{label} must be between 1 and {MAX_DURATION_MILLIS} milliseconds")
    return value


__all__ = (
    "DEFAULT_PRESS_DURATION_MILLIS",
    "DEFAULT_SWIPE_DURATION_MILLIS",
    "MAX_COORDINATE",
    "MAX_DURATION_MILLIS",
    "back",
    "click",
    "home",
    "long_click",
    "press",
    "swipe",
)
