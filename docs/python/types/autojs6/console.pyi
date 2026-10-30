# Type stub of the AutoJs6 Python Runtime package `autojs6` (mirrors app/src/main/python/autojs6/console.py).
# AutoJs6 tools/api-coverage/language_runtimes.py checks its names and signatures against the plugin.
"""Level-aware output written directly to the AutoJs6 Host console."""


def error(text: str) -> None:
    """Write one error-level line to the Host console."""
    ...


def log(text: str) -> None:
    """Write one debug-level line to the Host console."""
    ...


def warn(text: str) -> None:
    """Write one warning-level line to the Host console."""
    ...
