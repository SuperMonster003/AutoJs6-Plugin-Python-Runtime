"""Stable errors exposed by the AutoJs6 Python preview package."""


class AutoJs6Error(RuntimeError):
    """Base class for the bounded AutoJs6 preview API."""


class CapabilityUnavailableError(AutoJs6Error):
    """The host did not grant the requested frozen capability to this execution."""


class ProjectPathError(AutoJs6Error, ValueError):
    """A project-relative path is unsafe or does not name a regular project file."""


class ProjectReadLimitError(AutoJs6Error):
    """A project file exceeds the per-call read limit."""


__all__ = (
    "AutoJs6Error",
    "CapabilityUnavailableError",
    "ProjectPathError",
    "ProjectReadLimitError",
)
