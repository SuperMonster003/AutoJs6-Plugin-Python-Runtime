"""Bounded control over the current Host engine and scoped child scripts."""

from __future__ import annotations

import os
from typing import Any, NoReturn

from ._broker import _call, _expect_none, _expect_object, _protocol_error
from .files import MAX_PATH_BYTES, _normalize_path


INFO_SCHEMA = "autojs6-python-engine-info-v1"
LAUNCH_SCHEMA = "autojs6-python-engine-launch-v1"
MAX_SCRIPT_LAUNCHES = 16
MAX_ENGINE_NAME_BYTES = 256
MAX_SOURCE_NAME_BYTES = 1024


def current() -> dict[str, object]:
    """Return detached, path-safe metadata for the current Host Python engine."""
    value = _expect_object(_call("engines.current", {}), "engines.current")
    _validate_current(value)
    return dict(value)


def run(path: str | os.PathLike[str]) -> dict[str, object]:
    """Asynchronously start one scoped non-Python Host script and return its handle."""
    relative = _normalize_path(path)
    value = _expect_object(
        _call("engines.run", {"path": relative}),
        "engines.run",
    )
    _validate_launch(value, relative)
    return dict(value)


def stop_self() -> NoReturn:
    """Ask the Host to force-stop this engine; this call does not return normally."""
    _expect_none(_call("engines.stop_self", {}), "engines.stop_self")
    # The Host stop is posted outside the synchronous Binder dispatch so its response can be
    # encoded without deadlocking the current plugin call. Exit immediately if that response wins
    # the race; the queued Host force-stop remains authoritative and cannot be caught by user code.
    raise SystemExit(0)


def _validate_current(value: dict[str, Any]) -> None:
    if set(value) != {
        "schema",
        "id",
        "engineName",
        "sourceName",
        "entryPoint",
        "project",
        "startedAtMillis",
    }:
        _invalid("engines.current returned invalid fields")
    if value["schema"] != INFO_SCHEMA:
        _invalid("engines.current returned an invalid schema")
    if type(value["id"]) is not int or value["id"] < -1:
        _invalid("engines.current returned an invalid engine ID")
    if value["engineName"] != "python":
        _invalid("engines.current returned the wrong engine name")
    _bounded_text(value["sourceName"], "engines.current source name", MAX_SOURCE_NAME_BYTES)
    entry_point = _bounded_text(
        value["entryPoint"],
        "engines.current entry point",
        MAX_PATH_BYTES,
    )
    try:
        _normalize_path(entry_point)
    except (TypeError, ValueError) as error:
        raise _protocol_error("engines.current returned an invalid entry point", error)
    if type(value["project"]) is not bool:
        _invalid("engines.current returned an invalid project flag")
    if type(value["startedAtMillis"]) is not int or value["startedAtMillis"] < 0:
        _invalid("engines.current returned an invalid start time")


def _validate_launch(value: dict[str, Any], requested_path: str) -> None:
    if set(value) != {"schema", "id", "engineName", "sourceName", "path"}:
        _invalid("engines.run returned invalid fields")
    if value["schema"] != LAUNCH_SCHEMA:
        _invalid("engines.run returned an invalid schema")
    if type(value["id"]) is not int or value["id"] < 0:
        _invalid("engines.run returned an invalid execution ID")
    engine_name = _bounded_text(
        value["engineName"],
        "engines.run engine name",
        MAX_ENGINE_NAME_BYTES,
    )
    if engine_name == "python":
        _invalid("engines.run returned a nested Python execution")
    _bounded_text(value["sourceName"], "engines.run source name", MAX_SOURCE_NAME_BYTES)
    if value["path"] != requested_path:
        _invalid("engines.run returned a mismatched path")


def _bounded_text(value: Any, label: str, max_bytes: int) -> str:
    if type(value) is not str or not value:
        _invalid(f"{label} is invalid")
    try:
        size = len(value.encode("utf-8", "strict"))
    except UnicodeError as error:
        raise _protocol_error(f"{label} is not UTF-8", error)
    if size > max_bytes:
        _invalid(f"{label} exceeds its byte limit")
    return value


def _invalid(message: str) -> NoReturn:
    raise _protocol_error(message)


__all__ = (
    "INFO_SCHEMA",
    "LAUNCH_SCHEMA",
    "MAX_ENGINE_NAME_BYTES",
    "MAX_SCRIPT_LAUNCHES",
    "MAX_SOURCE_NAME_BYTES",
    "current",
    "run",
    "stop_self",
)
