"""M3 Host engines example; pass --stop-self to exercise deterministic self-stop."""

from __future__ import annotations

import sys

from autojs6 import engines, result


info = engines.current()
print("current engine:", info, flush=True)

if "--stop-self" in sys.argv:
    print("requesting self-stop", flush=True)
    engines.stop_self()

child = engines.run("m3_engines_child.js")
print("started child:", child, flush=True)
result.set({"current": info, "child": child})
