"""Frozen execution metadata for the current Python run."""

from ._context import _require_context


def snapshot() -> dict[str, object]:
    """Return a detached copy of the host-created execution snapshot."""
    return dict(_require_context().document["execution"])


__all__ = ("snapshot",)
