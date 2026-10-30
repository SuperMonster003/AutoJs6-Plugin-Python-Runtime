# Type stub of the AutoJs6 Python Runtime package `autojs6` (mirrors app/src/main/python/autojs6/clip.py).
# AutoJs6 tools/api-coverage/language_runtimes.py checks its names and signatures against the plugin.
"""Execution-scoped access to the AutoJs6 Host clipboard."""


def get() -> str:
    """Return the Host clipboard as text, or an empty string when it has no text."""
    ...


def set(text: str) -> None:
    """Replace the Host clipboard with bounded UTF-8 text."""
    ...
