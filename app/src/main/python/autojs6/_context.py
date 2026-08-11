"""Execution-local storage for the frozen host capability snapshot."""

from __future__ import annotations

import contextvars
import copy
import json
import os
import uuid
from dataclasses import dataclass
from typing import Any

from .errors import CapabilityUnavailableError


_MAX_SNAPSHOT_BYTES = 64 * 1024
_KNOWN_GRANTS = frozenset(
    {
        "app.snapshot.read",
        "device.snapshot.read",
        "project.files.read",
    }
)


@dataclass(frozen=True)
class _ExecutionContext:
    document: dict[str, Any] | None
    project_root: str | None


_ACTIVE: contextvars.ContextVar[_ExecutionContext | None] = contextvars.ContextVar(
    "autojs6_execution_context",
    default=None,
)


def _install_execution_context(
    encoded_snapshot: bytes,
    project_root: str | None,
) -> contextvars.Token[_ExecutionContext | None]:
    document = _decode_snapshot(encoded_snapshot) if encoded_snapshot else None
    normalized_root = os.path.realpath(os.fspath(project_root)) if project_root is not None else None
    if document is not None:
        declared_project = document["execution"]["project"]
        if declared_project != (normalized_root is not None):
            raise ValueError("Host capability project availability does not match the runtime workspace")
    return _ACTIVE.set(_ExecutionContext(document=document, project_root=normalized_root))


def _reset_execution_context(token: contextvars.Token[_ExecutionContext | None]) -> None:
    _ACTIVE.reset(token)


def _require_context() -> _ExecutionContext:
    context = _ACTIVE.get()
    if context is None or context.document is None:
        raise CapabilityUnavailableError(
            "AutoJs6 host capabilities are unavailable for this Python execution"
        )
    return context


def _require_grant(grant: str) -> _ExecutionContext:
    context = _require_context()
    if grant not in context.document["grants"]:
        raise CapabilityUnavailableError(f"AutoJs6 capability is unavailable: {grant}")
    return context


def _snapshot_section(grant: str, section: str) -> dict[str, Any]:
    context = _require_grant(grant)
    return copy.deepcopy(context.document[section])


def _project_context() -> _ExecutionContext:
    context = _require_grant("project.files.read")
    if context.project_root is None or not context.document["execution"]["project"]:
        raise CapabilityUnavailableError("Project files are unavailable for this Python execution")
    return context


def _decode_snapshot(encoded: bytes) -> dict[str, Any]:
    if not encoded or len(encoded) > _MAX_SNAPSHOT_BYTES:
        raise ValueError("Host capability snapshot size is invalid")
    try:
        text = encoded.decode("utf-8", "strict")
        document = json.loads(text, object_pairs_hook=_unique_object)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ValueError("Host capability snapshot is malformed") from error
    if not isinstance(document, dict):
        raise ValueError("Host capability snapshot must be an object")
    _exact_keys(document, {"schemaVersion", "execution", "grants", "app", "device"})
    if _integer(document["schemaVersion"]) != 1:
        raise ValueError("Host capability snapshot schema is unsupported")

    execution = _object(document["execution"], "execution")
    _exact_keys(execution, {"id", "entryPoint", "project"})
    execution_id = _text(execution["id"], "execution.id", allow_empty=False)
    try:
        if str(uuid.UUID(execution_id)) != execution_id:
            raise ValueError
    except ValueError as error:
        raise ValueError("Host capability execution ID is invalid") from error
    _text(execution["entryPoint"], "execution.entryPoint", allow_empty=False)
    _boolean(execution["project"], "execution.project")

    grants_value = document["grants"]
    if not isinstance(grants_value, list):
        raise ValueError("Host capability grants must be an array")
    grants = [_text(value, "grant", allow_empty=False) for value in grants_value]
    if len(grants) != len(set(grants)) or not set(grants).issubset(_KNOWN_GRANTS):
        raise ValueError("Host capability grants are duplicated or unsupported")
    expected_grants = {"app.snapshot.read", "device.snapshot.read"}
    if execution["project"]:
        expected_grants.add("project.files.read")
    if set(grants) != expected_grants:
        raise ValueError("Host capability grants do not match the execution snapshot")
    document["grants"] = frozenset(grants)

    app = _object(document["app"], "app")
    _exact_keys(app, {"packageName", "versionName", "versionCode", "debuggable"})
    _text(app["packageName"], "app.packageName", allow_empty=False)
    _text(app["versionName"], "app.versionName")
    if _integer(app["versionCode"]) <= 0:
        raise ValueError("Host version code must be positive")
    _boolean(app["debuggable"], "app.debuggable")

    device = _object(document["device"], "device")
    _exact_keys(device, {"sdkInt", "release", "manufacturer", "brand", "model", "supportedAbis"})
    sdk_int = _integer(device["sdkInt"])
    if not 1 <= sdk_int <= 1000:
        raise ValueError("Device API level is invalid")
    for name in ("release", "manufacturer", "brand", "model"):
        _text(device[name], f"device.{name}")
    abis = device["supportedAbis"]
    if not isinstance(abis, list) or not 1 <= len(abis) <= 8:
        raise ValueError("Device ABI snapshot is invalid")
    normalized_abis = [_text(value, "device ABI", allow_empty=False, maximum=128) for value in abis]
    if len(normalized_abis) != len(set(normalized_abis)):
        raise ValueError("Device ABI snapshot contains duplicates")
    return document


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Host capability snapshot contains a duplicate JSON key")
        result[key] = value
    return result


def _exact_keys(value: dict[str, Any], expected: set[str]) -> None:
    if set(value) != expected:
        raise ValueError("Host capability snapshot fields are missing or unsupported")


def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return value


def _text(
    value: Any,
    label: str,
    *,
    allow_empty: bool = True,
    maximum: int = 4096,
) -> str:
    if not isinstance(value, str) or (not allow_empty and not value):
        raise ValueError(f"{label} must be a string")
    if len(value.encode("utf-8")) > maximum or any(ord(character) < 0x20 for character in value):
        raise ValueError(f"{label} is unsafe or too long")
    return value


def _integer(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("Host capability field must be an integer")
    return value


def _boolean(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{label} must be a boolean")
    return value


__all__ = ()
