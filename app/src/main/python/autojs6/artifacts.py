"""Execution-scoped paths for optional bounded output artifacts."""

from __future__ import annotations

from ._context import _register_artifact_path


def path(relative_path: str) -> str:
    """Register a normalized logical path and return its Plugin-private file path."""
    return _register_artifact_path(relative_path)


__all__ = ("path",)
