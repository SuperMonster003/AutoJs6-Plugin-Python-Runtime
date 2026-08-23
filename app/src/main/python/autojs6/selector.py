"""Bounded UI-tree snapshots and explicit node actions through Host accessibility."""

from __future__ import annotations

import re
from typing import Any, NoReturn

from ._broker import (
    _call,
    _expect_boolean,
    _expect_object,
    _protocol_error,
    _require_text,
)


SNAPSHOT_SCHEMA = "autojs6-python-ui-tree-v1"
DEFAULT_SNAPSHOT_NODES = 64
MAX_SNAPSHOT_NODES = 128
DEFAULT_SNAPSHOT_DEPTH = 16
DEFAULT_FIND_NODES = 512
MAX_FIND_NODES = 1_024
MAX_DEPTH = 32
MAX_QUERY_TEXT_BYTES = 1_024
MAX_SET_TEXT_BYTES = 4 * 1_024
MAX_NODE_TEXT_CODE_POINTS = 256
MAX_RETAINED_NODES = 128

_NODE_ID = re.compile(r"node-([1-9][0-9]*)-([1-9][0-9]*)")
_NODE_TEXT_FIELDS = frozenset(
    ("text", "description", "resourceId", "className", "packageName")
)
_NODE_BOOLEAN_FIELDS = frozenset(
    (
        "clickable",
        "editable",
        "enabled",
        "focused",
        "selected",
        "checkable",
        "checked",
        "scrollable",
        "password",
        "visibleToUser",
    )
)
_NODE_KEYS = frozenset(
    (
        "id",
        "parentId",
        "depth",
        "childCount",
        *_NODE_TEXT_FIELDS,
        "bounds",
        *_NODE_BOOLEAN_FIELDS,
        "truncatedFields",
    )
)
_BOUNDS_KEYS = frozenset(("left", "top", "right", "bottom"))


def snapshot(
    max_nodes: int = DEFAULT_SNAPSHOT_NODES,
    max_depth: int = DEFAULT_SNAPSHOT_DEPTH,
) -> dict[str, object]:
    """Return one detached, bounded breadth-first snapshot of the active UI tree."""
    node_limit = _integer_limit(max_nodes, "Snapshot max_nodes", 1, MAX_SNAPSHOT_NODES)
    depth_limit = _integer_limit(max_depth, "Snapshot max_depth", 0, MAX_DEPTH)
    value = _expect_object(
        _call(
            "selector.snapshot",
            {"maxNodes": node_limit, "maxDepth": depth_limit},
        ),
        "selector.snapshot",
    )
    _validate_snapshot(value, node_limit, depth_limit)
    return value


def find(
    *,
    text: str | None = None,
    text_contains: str | None = None,
    description: str | None = None,
    description_contains: str | None = None,
    resource_id: str | None = None,
    class_name: str | None = None,
    clickable: bool | None = None,
    editable: bool | None = None,
    enabled: bool | None = None,
    scrollable: bool | None = None,
    max_nodes: int = DEFAULT_FIND_NODES,
    max_depth: int = MAX_DEPTH,
) -> dict[str, object] | None:
    """Return the first breadth-first node matching every supplied condition."""
    query: dict[str, object] = {}
    _add_query_text(query, "text", text, "Selector text")
    _add_query_text(query, "textContains", text_contains, "Selector text_contains")
    _add_query_text(query, "description", description, "Selector description")
    _add_query_text(
        query,
        "descriptionContains",
        description_contains,
        "Selector description_contains",
    )
    _add_query_text(query, "resourceId", resource_id, "Selector resource_id")
    _add_query_text(query, "className", class_name, "Selector class_name")
    _add_query_flag(query, "clickable", clickable, "Selector clickable")
    _add_query_flag(query, "editable", editable, "Selector editable")
    _add_query_flag(query, "enabled", enabled, "Selector enabled")
    _add_query_flag(query, "scrollable", scrollable, "Selector scrollable")
    if not query:
        raise ValueError("Selector find requires at least one condition")

    node_limit = _integer_limit(max_nodes, "Find max_nodes", 1, MAX_FIND_NODES)
    depth_limit = _integer_limit(max_depth, "Find max_depth", 0, MAX_DEPTH)
    value = _call(
        "selector.find",
        {
            "query": query,
            "maxNodes": node_limit,
            "maxDepth": depth_limit,
        },
    )
    if value is None:
        return None
    if type(value) is not dict:
        _invalid("selector.find returned a non-object node")
    _validate_node(value, require_detached_parent=True)
    return value


def click(node: str | dict[str, object]) -> bool:
    """Click one retained node returned by this execution's snapshot or find call."""
    node_id = _node_reference(node)
    return _expect_boolean(
        _call("selector.click", {"nodeId": node_id}),
        "selector.click",
    )


def set_text(node: str | dict[str, object], text: str) -> bool:
    """Set bounded text on one retained node and return the platform action result."""
    node_id = _node_reference(node)
    value = _require_text(text, "Selector text", max_bytes=MAX_SET_TEXT_BYTES)
    return _expect_boolean(
        _call("selector.set_text", {"nodeId": node_id, "text": value}),
        "selector.set_text",
    )


def _validate_snapshot(
    value: dict[str, Any],
    requested_nodes: int,
    requested_depth: int,
) -> None:
    if set(value) != {"schema", "generation", "truncated", "nodes"}:
        _invalid("selector.snapshot returned invalid fields")
    if value["schema"] != SNAPSHOT_SCHEMA:
        _invalid("selector.snapshot returned an invalid schema")
    generation = value["generation"]
    if type(generation) is not int or generation <= 0:
        _invalid("selector.snapshot returned an invalid generation")
    if type(value["truncated"]) is not bool:
        _invalid("selector.snapshot returned an invalid truncated flag")
    nodes = value["nodes"]
    if type(nodes) is not list or not 1 <= len(nodes) <= min(requested_nodes, MAX_SNAPSHOT_NODES):
        _invalid("selector.snapshot returned an invalid node count")

    depths: dict[str, int] = {}
    for index, node in enumerate(nodes):
        if type(node) is not dict:
            _invalid("selector.snapshot returned a non-object node")
        _validate_node(node)
        node_id = node["id"]
        match = _NODE_ID.fullmatch(node_id)
        if match is None or int(match.group(1)) != generation or node_id in depths:
            _invalid("selector.snapshot returned an invalid or duplicate node ID")
        parent_id = node["parentId"]
        depth = node["depth"]
        if parent_id is None:
            if index != 0 or depth != 0:
                _invalid("selector.snapshot returned an invalid root node")
        elif parent_id not in depths or depth != depths[parent_id] + 1:
            _invalid("selector.snapshot returned an invalid parent relationship")
        if depth > requested_depth:
            _invalid("selector.snapshot returned a node beyond the requested depth")
        depths[node_id] = depth


def _validate_node(value: dict[str, Any], *, require_detached_parent: bool = False) -> None:
    if set(value) != _NODE_KEYS:
        _invalid("selector returned invalid node fields")
    _validate_response_node_id(value["id"])
    parent_id = value["parentId"]
    if parent_id is not None:
        _validate_response_node_id(parent_id)
    if require_detached_parent and parent_id is not None:
        _invalid("selector.find returned a node with a parent reference")
    if type(value["depth"]) is not int or not 0 <= value["depth"] <= MAX_DEPTH:
        _invalid("selector returned an invalid node depth")
    if type(value["childCount"]) is not int or value["childCount"] < 0:
        _invalid("selector returned an invalid child count")

    for name in _NODE_TEXT_FIELDS:
        text = value[name]
        if text is not None:
            if type(text) is not str:
                _invalid(f"selector returned invalid {name}")
            try:
                text.encode("utf-8", "strict")
            except UnicodeError as error:
                raise _protocol_error(f"selector returned non-UTF-8 {name}", error)
            if len(text) > MAX_NODE_TEXT_CODE_POINTS:
                _invalid(f"selector returned oversized {name}")
    for name in _NODE_BOOLEAN_FIELDS:
        if type(value[name]) is not bool:
            _invalid(f"selector returned invalid {name}")

    bounds = value["bounds"]
    if type(bounds) is not dict or set(bounds) != _BOUNDS_KEYS:
        _invalid("selector returned invalid bounds")
    for name in _BOUNDS_KEYS:
        coordinate = bounds[name]
        if type(coordinate) is not int or not -(2**31) <= coordinate < 2**31:
            _invalid("selector returned an invalid bound coordinate")
    if bounds["right"] < bounds["left"] or bounds["bottom"] < bounds["top"]:
        _invalid("selector returned inverted bounds")

    truncated_fields = value["truncatedFields"]
    if type(truncated_fields) is not list or any(type(name) is not str for name in truncated_fields):
        _invalid("selector returned invalid truncated fields")
    if len(truncated_fields) != len(set(truncated_fields)) or not set(truncated_fields).issubset(
        _NODE_TEXT_FIELDS
    ):
        _invalid("selector returned duplicate or unsupported truncated fields")
    for name in truncated_fields:
        if value[name] is None or len(value[name]) != MAX_NODE_TEXT_CODE_POINTS:
            _invalid("selector returned an inconsistent truncated field")


def _add_query_text(
    query: dict[str, object],
    key: str,
    value: str | None,
    label: str,
) -> None:
    if value is not None:
        query[key] = _require_text(
            value,
            label,
            allow_empty=False,
            max_bytes=MAX_QUERY_TEXT_BYTES,
        )


def _add_query_flag(
    query: dict[str, object],
    key: str,
    value: bool | None,
    label: str,
) -> None:
    if value is None:
        return
    if type(value) is not bool:
        raise TypeError(f"{label} must be a boolean")
    query[key] = value


def _node_reference(value: str | dict[str, object]) -> str:
    if type(value) is str:
        node_id = value
    elif type(value) is dict:
        node_id = value.get("id")
        if type(node_id) is not str:
            raise TypeError("Selector node mapping must contain a text ID")
    else:
        raise TypeError("Selector node must be an ID or node dictionary")
    node_id = _require_text(node_id, "Selector node ID", allow_empty=False, max_bytes=64)
    if _NODE_ID.fullmatch(node_id) is None:
        raise ValueError("Selector node ID is invalid")
    return node_id


def _validate_response_node_id(value: Any) -> None:
    if type(value) is not str:
        _invalid("selector returned an invalid node ID")
    try:
        encoded_size = len(value.encode("utf-8", "strict"))
    except UnicodeError as error:
        raise _protocol_error("selector returned a non-UTF-8 node ID", error)
    if encoded_size > 64:
        _invalid("selector returned an invalid node ID")
    if _NODE_ID.fullmatch(value) is None:
        _invalid("selector returned an invalid node ID")


def _integer_limit(value: int, label: str, minimum: int, maximum: int) -> int:
    if type(value) is not int:
        raise TypeError(f"{label} must be an integer")
    if not minimum <= value <= maximum:
        raise ValueError(f"{label} must be between {minimum} and {maximum}")
    return value


def _invalid(message: str) -> NoReturn:
    raise _protocol_error(message)


__all__ = (
    "DEFAULT_FIND_NODES",
    "DEFAULT_SNAPSHOT_DEPTH",
    "DEFAULT_SNAPSHOT_NODES",
    "MAX_DEPTH",
    "MAX_FIND_NODES",
    "MAX_NODE_TEXT_CODE_POINTS",
    "MAX_QUERY_TEXT_BYTES",
    "MAX_RETAINED_NODES",
    "MAX_SET_TEXT_BYTES",
    "MAX_SNAPSHOT_NODES",
    "SNAPSHOT_SCHEMA",
    "click",
    "find",
    "set_text",
    "snapshot",
)
