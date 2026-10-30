# Type stub of the AutoJs6 Python Runtime package `autojs6` (mirrors app/src/main/python/autojs6/selector.py).
# AutoJs6 tools/api-coverage/language_runtimes.py checks its names and signatures against the plugin.
"""Bounded UI-tree snapshots and explicit node actions through Host accessibility."""

from typing import Final

DEFAULT_FIND_NODES: Final[int]
DEFAULT_SNAPSHOT_DEPTH: Final[int]
DEFAULT_SNAPSHOT_NODES: Final[int]
MAX_DEPTH: Final[int]
MAX_FIND_NODES: Final[int]
MAX_NODE_TEXT_CODE_POINTS: Final[int]
MAX_QUERY_TEXT_BYTES: Final[int]
MAX_RETAINED_NODES: Final[int]
MAX_SET_TEXT_BYTES: Final[int]
MAX_SNAPSHOT_NODES: Final[int]
SNAPSHOT_SCHEMA: Final[str]


def click(node: str | dict[str, object]) -> bool:
    """Click one retained node returned by this execution's snapshot or find call."""
    ...


def find(
    *,
    text: str | None = ...,
    text_contains: str | None = ...,
    description: str | None = ...,
    description_contains: str | None = ...,
    resource_id: str | None = ...,
    class_name: str | None = ...,
    clickable: bool | None = ...,
    editable: bool | None = ...,
    enabled: bool | None = ...,
    scrollable: bool | None = ...,
    max_nodes: int = ...,
    max_depth: int = ...,
) -> dict[str, object] | None:
    """Return the first breadth-first node matching every supplied condition."""
    ...


def set_text(node: str | dict[str, object], text: str) -> bool:
    """Set bounded text on one retained node and return the platform action result."""
    ...


def snapshot(max_nodes: int = ..., max_depth: int = ...) -> dict[str, object]:
    """Return one detached, bounded breadth-first snapshot of the active UI tree."""
    ...
