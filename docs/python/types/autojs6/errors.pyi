# Type stub of the AutoJs6 Python Runtime package `autojs6` (mirrors app/src/main/python/autojs6/errors.py).
# AutoJs6 tools/api-coverage/language_runtimes.py checks its names, signatures and constant values against the plugin.
"""Stable errors exposed by the AutoJs6 Python preview package."""


class AutoJs6Error(RuntimeError):
    """Base class for the bounded AutoJs6 preview API."""


class CapabilityUnavailableError(AutoJs6Error):
    """The host did not grant the requested capability to this execution."""


class HostCapabilityError(AutoJs6Error):
    """A live Host capability failed with a stable protocol error code."""
    code: str

    def __init__(self, code: str, message: str) -> None: ...


class ProjectPathError(AutoJs6Error, ValueError):
    """A project-relative path is unsafe or does not name a regular project file."""


class ProjectReadLimitError(AutoJs6Error):
    """A project file exceeds the per-call read limit."""


class ResultAlreadySetError(AutoJs6Error):
    """The one explicit structured result slot was already populated."""


class ResultSerializationError(AutoJs6Error, TypeError):
    """A value cannot be represented as strict finite JSON."""


class ResultLimitError(AutoJs6Error):
    """The encoded structured result exceeds its execution-scoped byte limit."""


class ArtifactPathError(AutoJs6Error, ValueError):
    """An output artifact path is unsafe or not normalized."""


class ArtifactLimitError(AutoJs6Error):
    """An output artifact declaration exceeds an execution-scoped limit."""
