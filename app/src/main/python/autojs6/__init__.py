"""Execution-scoped AutoJs6 data, result and live Host capability APIs."""

from . import app, artifacts, clip, device, execution, project, result
from ._broker import _call, _expect_none, _require_text
from .errors import (
    AutoJs6Error,
    ArtifactLimitError,
    ArtifactPathError,
    CapabilityUnavailableError,
    HostCapabilityError,
    ProjectPathError,
    ProjectReadLimitError,
    ResultAlreadySetError,
    ResultLimitError,
    ResultSerializationError,
)


def toast(text: str) -> None:
    """Show one bounded toast through the AutoJs6 Host."""
    value = _require_text(text, "Toast text")
    _expect_none(_call("toast.show", {"text": value}), "toast.show")


__all__ = (
    "app",
    "artifacts",
    "clip",
    "device",
    "execution",
    "project",
    "result",
    "toast",
    "AutoJs6Error",
    "ArtifactLimitError",
    "ArtifactPathError",
    "CapabilityUnavailableError",
    "HostCapabilityError",
    "ProjectPathError",
    "ProjectReadLimitError",
    "ResultAlreadySetError",
    "ResultLimitError",
    "ResultSerializationError",
)
