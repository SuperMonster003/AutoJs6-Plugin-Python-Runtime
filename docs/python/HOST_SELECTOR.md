# Host selector and UI-tree snapshots

`autojs6.selector` exposes a bounded, execution-scoped view of the active
Android accessibility tree. All values cross the protocol 1.5 broker as strict
JSON data. Android `AccessibilityNodeInfo`, `Context`, service, callback, and raw
Binder objects never enter the Python process.

## Prerequisite

The user must enable the AutoJs6 accessibility service before using this API.
The API never enables the service, opens settings, or changes an accessibility
preference. A missing, disconnected, non-operational, or rootless service raises
`CapabilityUnavailableError` without performing an action.

## Public API

```python
from autojs6 import selector

selector.snapshot(
    max_nodes: int = 64,
    max_depth: int = 16,
) -> dict[str, object]

selector.find(
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
    max_nodes: int = 512,
    max_depth: int = 32,
) -> dict[str, object] | None

selector.click(node: str | dict[str, object]) -> bool
selector.set_text(node: str | dict[str, object], text: str) -> bool
```

`find` combines every supplied condition with logical AND and returns the first
breadth-first match. Text, description, resource ID, and class name comparisons
are case-sensitive. `*_contains` performs literal substring matching; there is
no implicit regular expression, polling, timeout, ancestor fallback, or retry.
At least one condition is required.

`click` and `set_text` accept either a node mapping returned by `snapshot` or
`find`, or that mapping's opaque `id` string. They return the actual Android
action result. A platform `false` result remains `False` and is not retried.
`set_text` does not implicitly focus the node and accepts an empty string for an
explicit clear operation.

## Snapshot schema

`snapshot` returns this top-level mapping:

```text
{
  "schema": "autojs6-python-ui-tree-v1",
  "generation": positive integer,
  "truncated": boolean,
  "nodes": [node, ...]
}
```

Nodes are breadth-first and contain only detached JSON fields:

```text
id, parentId, depth, childCount,
text, description, resourceId, className, packageName,
bounds {left, top, right, bottom},
clickable, editable, enabled, focused, selected,
checkable, checked, scrollable, password, visibleToUser,
truncatedFields
```

`parentId` is `None` only for the snapshot root. A node returned directly by
`find` is detached from a returned tree and also has `parentId=None`; its `depth`
still records the traversal depth. Nullable Android text fields remain `None`.
Every present text-like node field is capped at 256 Unicode code points. A field
which was shortened is named in `truncatedFields`, so truncation is never silent.

## Bounds and honest absence

- A snapshot defaults to 64 nodes and depth 16, accepts at most 128 nodes and
  depth 32, and caps its JSON value at 48 KiB. `truncated=True` means a node,
  depth, or payload boundary stopped traversal.
- `find` scans at most 512 nodes by default and at most 1024 when requested. Its
  depth is at most 32. A complete bounded scan with no match returns `None`.
- If `find` reaches its node or depth boundary before it can prove absence, it
  raises `HostCapabilityError` with code `SELECTOR_SCAN_LIMIT_EXCEEDED` instead
  of returning a misleading `None`.
- Every selector query string is non-empty and at most 1024 UTF-8 bytes.
  `set_text` accepts at most 4096 UTF-8 bytes.
- At most 128 native node references are retained. The ordinary broker limits
  of 1024 calls, 64 KiB per request/response, and 5 seconds for a Host action
  continue to apply.

## Node lifetime

Node IDs are opaque capabilities, not serialized Android handles. They are
valid only in the current Python execution and only while the Host retains and
can refresh the underlying node.

- Every new `snapshot` starts a generation and invalidates every older node.
- `find` adds its returned node to the current retained set. Once the 128-node
  limit is full, the oldest retained node is recycled and becomes stale.
- A window change may make a retained Android node unrefreshable.
- Terminal success/failure, cancellation, Binder loss, or broker close recycles
  all retained nodes.

Using an unknown, evicted, invalidated, or unrefreshable ID raises
`HostCapabilityError` with code `STALE_NODE`. IDs cannot be used by another
execution and are never replayed after cancellation.

See [`m3_selector.py`](../../examples/python/m3_selector.py) for a guarded
example, [`HOST_AUTOMATOR.md`](HOST_AUTOMATOR.md) for coordinate/global actions,
and [`PYTHON_SEMANTICS_CONTRACT.md`](PYTHON_SEMANTICS_CONTRACT.md) for normative
broker and execution semantics.
