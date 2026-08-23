"""AutoJs6 application metadata and low-risk Host launch operations."""

from ._broker import _call, _expect_boolean, _require_text
from ._context import _snapshot_section


def snapshot() -> dict[str, object]:
    """Return a detached copy of the frozen host application snapshot."""
    return _snapshot_section("app.snapshot.read", "app")


def launch(package_name: str) -> bool:
    """Launch an installed package by its Android package name."""
    package = _require_text(package_name, "Package name", allow_empty=False)
    return _expect_boolean(_call("app.launch", {"package": package}), "app.launch")


def launch_app(name: str) -> bool:
    """Launch an installed application by its visible label."""
    label = _require_text(name, "Application name", allow_empty=False)
    return _expect_boolean(_call("app.launch_app", {"name": label}), "app.launch_app")


def open_url(url: str) -> bool:
    """Open one HTTP or HTTPS URL through the Host."""
    value = _require_text(url, "URL", allow_empty=False)
    return _expect_boolean(_call("app.open_url", {"url": value}), "app.open_url")


__all__ = ("launch", "launch_app", "open_url", "snapshot")
