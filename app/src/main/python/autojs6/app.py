"""Read-only AutoJs6 application metadata."""

from ._context import _snapshot_section


def snapshot() -> dict[str, object]:
    """Return a detached copy of the frozen host application snapshot."""
    return _snapshot_section("app.snapshot.read", "app")


__all__ = ("snapshot",)
