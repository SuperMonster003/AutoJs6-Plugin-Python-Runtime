# Type stub of the AutoJs6 Python Runtime package `autojs6` (mirrors app/src/main/python/autojs6/app.py).
# AutoJs6 tools/api-coverage/language_runtimes.py checks its names and signatures against the plugin.
"""AutoJs6 application metadata and low-risk Host launch operations."""


def launch(package_name: str) -> bool:
    """Launch an installed package by its Android package name."""
    ...


def launch_app(name: str) -> bool:
    """Launch an installed application by its visible label."""
    ...


def open_url(url: str) -> bool:
    """Open one HTTP or HTTPS URL through the Host."""
    ...


def snapshot() -> dict[str, object]:
    """Return a detached copy of the frozen host application snapshot."""
    ...
