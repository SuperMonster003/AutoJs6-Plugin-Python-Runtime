"""Small, frozen and read-only AutoJs6 API for the R5 Python preview."""

from . import app, device, execution, project
from .errors import (
    AutoJs6Error,
    CapabilityUnavailableError,
    ProjectPathError,
    ProjectReadLimitError,
)


__all__ = (
    "app",
    "device",
    "execution",
    "project",
    "AutoJs6Error",
    "CapabilityUnavailableError",
    "ProjectPathError",
    "ProjectReadLimitError",
)
