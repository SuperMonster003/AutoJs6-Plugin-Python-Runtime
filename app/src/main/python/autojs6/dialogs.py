"""Bounded foreground dialogs owned and rendered by the AutoJs6 Host."""

from __future__ import annotations

from collections.abc import Sequence

from ._broker import (
    _call,
    _expect_boolean,
    _expect_none,
    _protocol_error,
    _require_text,
)


DEFAULT_TITLE = "AutoJs6 Python"
MAX_TITLE_BYTES = 256
MAX_TEXT_BYTES = 4 * 1024
MAX_PROMPT_REPLY_BYTES = 32 * 1024
MAX_ITEMS = 64
MAX_ITEM_BYTES = 1024
MAX_TOTAL_ITEM_BYTES = 32 * 1024


def alert(text: str, *, title: str = DEFAULT_TITLE) -> None:
    """Show a foreground alert and block until it is acknowledged or dismissed."""
    _expect_none(
        _call(
            "dialogs.alert",
            {"title": _title(title), "text": _text(text)},
        ),
        "dialogs.alert",
    )


def confirm(text: str, *, title: str = DEFAULT_TITLE) -> bool:
    """Return ``True`` only when the foreground confirmation is accepted."""
    return _expect_boolean(
        _call(
            "dialogs.confirm",
            {"title": _title(title), "text": _text(text)},
        ),
        "dialogs.confirm",
    )


def prompt(
    text: str,
    *,
    default: str = "",
    title: str = DEFAULT_TITLE,
) -> str | None:
    """Return entered foreground text, or ``None`` when the dialog is cancelled."""
    value = _call(
        "dialogs.prompt",
        {
            "title": _title(title),
            "text": _text(text),
            "default": _require_text(
                default,
                "Dialog default value",
                max_bytes=MAX_PROMPT_REPLY_BYTES,
            ),
        },
    )
    if value is None:
        return None
    if not isinstance(value, str):
        raise _protocol_error("dialogs.prompt returned a non-text value")
    _require_text(value, "Dialog prompt result", max_bytes=MAX_PROMPT_REPLY_BYTES)
    return value


def select(
    items: Sequence[str],
    *,
    title: str = DEFAULT_TITLE,
) -> int | None:
    """Return the selected zero-based index, or ``None`` when cancelled."""
    bounded_items = _items(items)
    value = _call(
        "dialogs.select",
        {"title": _title(title), "items": bounded_items},
    )
    if value is None:
        return None
    if type(value) is not int or not 0 <= value < len(bounded_items):
        raise _protocol_error("dialogs.select returned an invalid item index")
    return value


def _title(value: str) -> str:
    return _require_text(
        value,
        "Dialog title",
        allow_empty=False,
        max_bytes=MAX_TITLE_BYTES,
    )


def _text(value: str) -> str:
    return _require_text(value, "Dialog text", max_bytes=MAX_TEXT_BYTES)


def _items(values: Sequence[str]) -> list[str]:
    if isinstance(values, (str, bytes, bytearray)) or not isinstance(values, Sequence):
        raise TypeError("Dialog items must be a sequence of text values")
    items = list(values)
    if not 1 <= len(items) <= MAX_ITEMS:
        raise ValueError(f"Dialog item count must be between 1 and {MAX_ITEMS}")
    total_bytes = 0
    bounded: list[str] = []
    for value in items:
        item = _require_text(
            value,
            "Dialog item",
            allow_empty=False,
            max_bytes=MAX_ITEM_BYTES,
        )
        total_bytes += len(item.encode("utf-8", "strict"))
        if total_bytes > MAX_TOTAL_ITEM_BYTES:
            raise ValueError(
                f"Dialog items exceed the {MAX_TOTAL_ITEM_BYTES}-byte aggregate limit"
            )
        bounded.append(item)
    return bounded


__all__ = (
    "DEFAULT_TITLE",
    "MAX_ITEMS",
    "MAX_ITEM_BYTES",
    "MAX_PROMPT_REPLY_BYTES",
    "MAX_TEXT_BYTES",
    "MAX_TITLE_BYTES",
    "MAX_TOTAL_ITEM_BYTES",
    "alert",
    "confirm",
    "prompt",
    "select",
)
