"""Explicit, bounded structured result for one Python execution."""

from __future__ import annotations

from typing import Any

from ._context import _set_structured_result


def set(value: Any) -> None:
    """Set exactly one strict JSON-compatible result, independently of stdout."""
    _set_structured_result(value)


__all__ = ("set",)
