"""Measure Host-engine start to the first practical Python statement."""

from __future__ import annotations

import time


first_python_wall_millis = time.time_ns() // 1_000_000

import os

from autojs6 import engines, result


engine = engines.current()
engine_started_at_millis = int(engine["startedAtMillis"])
if engine_started_at_millis <= 0:
    raise RuntimeError("Host did not provide a usable engine start timestamp")
if first_python_wall_millis < engine_started_at_millis:
    raise RuntimeError("Wall clock moved backwards during Python launch")

startup_millis = first_python_wall_millis - engine_started_at_millis
plugin_pid = os.getpid()
engine_id = int(engine["id"])

print(
    f"startup_probe_ms={startup_millis} plugin_pid={plugin_pid} engine_id={engine_id}",
    flush=True,
)
result.set(
    {
        "schema": "autojs6-python-startup-probe-v1",
        "startupMillis": startup_millis,
        "pluginPid": plugin_pid,
        "engineId": engine_id,
        "engineStartedAtMillis": engine_started_at_millis,
        "firstPythonWallMillis": first_python_wall_millis,
    }
)
