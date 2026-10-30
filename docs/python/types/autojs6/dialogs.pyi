# Type stub of the AutoJs6 Python Runtime package `autojs6` (mirrors app/src/main/python/autojs6/dialogs.py).
# AutoJs6 tools/api-coverage/language_runtimes.py checks its names, signatures and constant values against the plugin.
"""Bounded foreground dialogs owned and rendered by the AutoJs6 Host."""

from collections.abc import Sequence
from typing import Final

DEFAULT_TITLE: Final = "AutoJs6 Python"
MAX_ITEMS: Final = 64
MAX_ITEM_BYTES: Final = 1024
MAX_PROMPT_REPLY_BYTES: Final = 32768
MAX_TEXT_BYTES: Final = 4096
MAX_TITLE_BYTES: Final = 256
MAX_TOTAL_ITEM_BYTES: Final = 32768


def alert(text: str, *, title: str = ...) -> None:
    """Show a foreground alert and block until it is acknowledged or dismissed."""
    ...


def confirm(text: str, *, title: str = ...) -> bool:
    """Return ``True`` only when the foreground confirmation is accepted."""
    ...


def prompt(text: str, *, default: str = ..., title: str = ...) -> str | None:
    """Return entered foreground text, or ``None`` when the dialog is cancelled."""
    ...


def select(items: Sequence[str], *, title: str = ...) -> int | None:
    """Return the selected zero-based index, or ``None`` when cancelled."""
    ...
