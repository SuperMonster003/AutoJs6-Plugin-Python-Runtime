# Type stub of the AutoJs6 Python Runtime package `autojs6` (mirrors app/src/main/python/autojs6/__init__.py).
# AutoJs6 tools/api-coverage/language_runtimes.py checks its names, signatures and constant values against the plugin.
"""Execution-scoped AutoJs6 data, result and live Host capability APIs."""

from . import app as app
from . import artifacts as artifacts
from . import automator as automator
from . import clip as clip
from . import console as console
from . import device as device
from . import dialogs as dialogs
from . import engines as engines
from . import execution as execution
from . import files as files
from . import images as images
from . import ocr as ocr
from . import project as project
from . import result as result
from . import selector as selector
from .errors import (
    AutoJs6Error as AutoJs6Error,
    ArtifactLimitError as ArtifactLimitError,
    ArtifactPathError as ArtifactPathError,
    CapabilityUnavailableError as CapabilityUnavailableError,
    HostCapabilityError as HostCapabilityError,
    ProjectPathError as ProjectPathError,
    ProjectReadLimitError as ProjectReadLimitError,
    ResultAlreadySetError as ResultAlreadySetError,
    ResultLimitError as ResultLimitError,
    ResultSerializationError as ResultSerializationError,
)


def notice(text: str) -> None:
    """Post one execution-tagged notification through the AutoJs6 Host."""
    ...


def toast(text: str) -> None:
    """Show one bounded toast through the AutoJs6 Host."""
    ...
