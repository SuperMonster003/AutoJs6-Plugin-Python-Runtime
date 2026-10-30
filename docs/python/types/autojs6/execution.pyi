# Type stub of the AutoJs6 Python Runtime package `autojs6` (mirrors app/src/main/python/autojs6/execution.py).
# AutoJs6 tools/api-coverage/language_runtimes.py checks its names and signatures against the plugin.
"""Frozen execution metadata for the current Python run."""


def snapshot() -> dict[str, object]:
    """Return a detached copy of the host-created execution snapshot."""
    ...
