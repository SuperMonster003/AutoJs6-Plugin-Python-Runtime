# Type stub of the AutoJs6 Python Runtime package `autojs6` (mirrors app/src/main/python/autojs6/device.py).
# AutoJs6 tools/api-coverage/language_runtimes.py checks its names and signatures against the plugin.
"""Frozen metadata and live, identifier-free AutoJs6 device state."""


def info() -> dict[str, object]:
    """Read current battery, screen brightness and volume state from the Host."""
    ...


def snapshot() -> dict[str, object]:
    """Return a detached copy of the frozen device snapshot."""
    ...
