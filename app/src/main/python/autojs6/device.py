"""Frozen metadata and live, identifier-free AutoJs6 device state."""

from __future__ import annotations

import math
from typing import Any

from ._broker import _call, _expect_object
from ._context import _snapshot_section


_SCHEMA = "autojs6-python-device-info-v1"


def snapshot() -> dict[str, object]:
    """Return a detached copy of the frozen device snapshot."""
    return _snapshot_section("device.snapshot.read", "device")


def info() -> dict[str, object]:
    """Read current battery, screen brightness and volume state from the Host."""
    value = _expect_object(_call("device.info", {}), "device.info")
    _validate_info(value)
    return value


def _validate_info(value: dict[str, Any]) -> None:
    if set(value) != {"schema", "battery", "screen", "volume"}:
        _invalid_info("top-level fields")
    if value["schema"] != _SCHEMA:
        _invalid_info("schema")

    battery = _nested(value["battery"], "battery", {"percent", "charging"})
    percent = battery["percent"]
    if type(percent) not in (int, float) or not math.isfinite(percent) or not 0 <= percent <= 100:
        _invalid_info("battery.percent")
    if type(battery["charging"]) is not bool:
        _invalid_info("battery.charging")

    screen = _nested(value["screen"], "screen", {"on", "brightness"})
    if type(screen["on"]) is not bool:
        _invalid_info("screen.on")
    if type(screen["brightness"]) is not int or screen["brightness"] < -1:
        _invalid_info("screen.brightness")

    volume = _nested(
        value["volume"],
        "volume",
        {"music", "notification", "alarm"},
    )
    for stream in ("music", "notification", "alarm"):
        level = _nested(volume[stream], f"volume.{stream}", {"current", "max"})
        current, maximum = level["current"], level["max"]
        if (
            type(current) is not int
            or type(maximum) is not int
            or current < 0
            or maximum < 0
            or current > maximum
        ):
            _invalid_info(f"volume.{stream}")


def _nested(value: Any, label: str, fields: set[str]) -> dict[str, Any]:
    if type(value) is not dict or set(value) != fields:
        _invalid_info(f"{label} fields")
    return value


def _invalid_info(field: str) -> None:
    from ._broker import _protocol_error

    raise _protocol_error(f"device.info returned invalid {field}")


__all__ = ("info", "snapshot")
