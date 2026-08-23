# Host automator actions

`autojs6.automator` is the first M3 automation slice. It performs a small,
execution-scoped set of accessibility actions in the AutoJs6 Host instead of
inside the Python Runtime plugin process.

## Prerequisite

The user must enable the AutoJs6 accessibility service before running an action.
The Python API never enables the service, opens Android settings, or changes an
accessibility preference. If the service is missing, disconnected, or not yet
operational, the call raises `CapabilityUnavailableError` with no device action.

## Public API

```python
from autojs6 import automator

automator.click(x: int, y: int) -> bool
automator.long_click(x: int, y: int) -> bool
automator.press(x: int, y: int, duration_ms: int = 100) -> bool
automator.swipe(
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    duration_ms: int = 300,
) -> bool
automator.back() -> bool
automator.home() -> bool
```

The returned boolean is the actual Host/platform action result. The facade does
not convert a rejected action to success and does not retry it. Coordinate and
global actions can change the foreground application immediately, so scripts
should treat every successful call as an externally visible side effect.

## Bounds

- Every coordinate is a strict Python `int` from `0` through `1_000_000`.
  `bool` is rejected even though it is an `int` subclass in Python.
- `press` and `swipe` durations are strict integers from `1` through `4_000`
  milliseconds.
- The Python facade validates the values before dispatch, and the Host repeats
  the same bounds before touching accessibility.
- The ordinary protocol 1.5 execution quota of 1024 Host calls and 64 KiB
  request/response limits still apply.

Invalid local argument types raise `TypeError`; out-of-range values raise
`ValueError`. Host accessibility unavailability raises
`CapabilityUnavailableError`. Other stable Host failures use
`HostCapabilityError`.

## Scope and limitations

Each call travels through the protocol 1.5 pure-data broker and is bound to the
current public Python execution, plugin UID, request UUID, and monotonic call ID.
The broker is revoked at terminal, cancellation, or connection loss. Python does
not receive an Android `Context`, accessibility service object, node, callback,
or raw Binder handle.

The complementary bounded selector, UI-tree snapshot, node click, and text
setting surface is documented in [`HOST_SELECTOR.md`](HOST_SELECTOR.md).
Screenshot, image matching, and OCR remain separate Roadmap items because they
require image and artifact data models in addition to the action channel.

See [`m3_automator.py`](../../examples/python/m3_automator.py) for a minimal
script and [`PYTHON_SEMANTICS_CONTRACT.md`](PYTHON_SEMANTICS_CONTRACT.md) for the
normative execution and error semantics.
