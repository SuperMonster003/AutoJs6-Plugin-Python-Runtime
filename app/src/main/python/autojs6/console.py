"""Level-aware output written directly to the AutoJs6 Host console."""

from ._broker import _call, _expect_none, _require_text


def log(text: str) -> None:
    """Write one debug-level line to the Host console."""
    _write("console.log", text)


def warn(text: str) -> None:
    """Write one warning-level line to the Host console."""
    _write("console.warn", text)


def error(text: str) -> None:
    """Write one error-level line to the Host console."""
    _write("console.error", text)


def _write(capability: str, text: str) -> None:
    value = _require_text(text, "Console text")
    _expect_none(_call(capability, {"text": value}), capability)


__all__ = ("error", "log", "warn")
