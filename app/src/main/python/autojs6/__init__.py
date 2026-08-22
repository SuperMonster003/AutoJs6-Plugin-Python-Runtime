"""Small execution-scoped AutoJs6 API for bounded host data and explicit results."""

from . import app, artifacts, device, execution, project, result
from .errors import (
    AutoJs6Error,
    ArtifactLimitError,
    ArtifactPathError,
    CapabilityUnavailableError,
    ProjectPathError,
    ProjectReadLimitError,
    ResultAlreadySetError,
    ResultLimitError,
    ResultSerializationError,
)


__all__ = (
    "app",
    "artifacts",
    "device",
    "execution",
    "project",
    "result",
    "AutoJs6Error",
    "ArtifactLimitError",
    "ArtifactPathError",
    "CapabilityUnavailableError",
    "ProjectPathError",
    "ProjectReadLimitError",
    "ResultAlreadySetError",
    "ResultLimitError",
    "ResultSerializationError",
)
