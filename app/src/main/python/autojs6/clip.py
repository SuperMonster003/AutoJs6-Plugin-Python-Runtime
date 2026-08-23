"""Execution-scoped access to the AutoJs6 Host clipboard."""

from ._broker import _call, _expect_none, _expect_text, _require_text


def get() -> str:
    """Return the Host clipboard as text, or an empty string when it has no text."""
    return _expect_text(_call("clip.get", {}), "clip.get")


def set(text: str) -> None:
    """Replace the Host clipboard with bounded UTF-8 text."""
    value = _require_text(text, "Clipboard text")
    _expect_none(_call("clip.set", {"text": value}), "clip.set")


__all__ = ("get", "set")
