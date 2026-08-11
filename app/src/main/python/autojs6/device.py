"""Coarse, identifier-free device metadata frozen before execution."""

from ._context import _snapshot_section


def snapshot() -> dict[str, object]:
    """Return a detached copy of the frozen device snapshot."""
    return _snapshot_section("device.snapshot.read", "device")


__all__ = ("snapshot",)
