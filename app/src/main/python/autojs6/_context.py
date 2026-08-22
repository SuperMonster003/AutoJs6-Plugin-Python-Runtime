"""Execution-local storage for the frozen host capability snapshot."""

from __future__ import annotations

import contextvars
import copy
import json
import math
import os
import re
import unicodedata
import uuid
from dataclasses import dataclass, field
from typing import Any

from .errors import (
    ArtifactLimitError,
    ArtifactPathError,
    CapabilityUnavailableError,
    ResultAlreadySetError,
    ResultLimitError,
    ResultSerializationError,
)


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
    result_state: _ExecutionResultState | None


@dataclass
class _ExecutionResultState:
    output_root: str | None
    max_structured_json_bytes: int
    max_artifacts: int
    max_artifact_path_bytes: int
    structured_json: str | None = None
    structured_json_set: bool = False
    artifact_paths: list[str] = field(default_factory=list)
    artifact_path_set: set[str] = field(default_factory=set)


_ACTIVE: contextvars.ContextVar[_ExecutionContext | None] = contextvars.ContextVar(
    "autojs6_execution_context",
    default=None,
)


def _install_execution_context(
    encoded_snapshot: bytes,
    project_root: str | None,
    output_root: str | None = None,
    max_structured_json_bytes: int = 0,
    max_artifacts: int = 0,
    max_artifact_path_bytes: int = 0,
) -> contextvars.Token[_ExecutionContext | None]:
    document = _decode_snapshot(encoded_snapshot) if encoded_snapshot else None
    normalized_root = os.path.realpath(os.fspath(project_root)) if project_root is not None else None
    if document is not None:
        declared_project = document["execution"]["project"]
        if declared_project != (normalized_root is not None):
            raise ValueError("Host capability project availability does not match the runtime workspace")
    result_state = _create_result_state(
        output_root,
        max_structured_json_bytes,
        max_artifacts,
        max_artifact_path_bytes,
    )
    return _ACTIVE.set(
        _ExecutionContext(
            document=document,
            project_root=normalized_root,
            result_state=result_state,
        )
    )


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


def _set_structured_result(value: Any) -> None:
    state = _require_result_state("Structured JSON results")
    if state.max_structured_json_bytes <= 0:
        raise CapabilityUnavailableError(
            "Structured JSON results are unavailable for this Python execution"
        )
    if state.structured_json_set:
        raise ResultAlreadySetError("The structured JSON result was already set")
    try:
        _require_json_value(value, set(), 0)
        encoded = json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        size = len(encoded.encode("utf-8", "strict"))
    except (TypeError, ValueError, UnicodeError, RecursionError) as error:
        raise ResultSerializationError(
            "Structured result must contain only finite JSON-compatible values"
        ) from error
    if size > state.max_structured_json_bytes:
        raise ResultLimitError(
            "Structured JSON result exceeds the execution byte limit"
        )
    state.structured_json = encoded
    state.structured_json_set = True


def _register_artifact_path(value: str) -> str:
    state = _require_result_state("Output artifacts")
    if state.max_artifacts <= 0 or state.output_root is None:
        raise CapabilityUnavailableError(
            "Output artifacts are unavailable for this Python execution"
        )
    relative = _artifact_relative_path(value, state.max_artifact_path_bytes)
    if relative not in state.artifact_path_set:
        if len(state.artifact_paths) >= state.max_artifacts:
            raise ArtifactLimitError("Output artifact count exceeds the execution limit")
        state.artifact_path_set.add(relative)
        state.artifact_paths.append(relative)
    target = os.path.join(state.output_root, *relative.split("/"))
    parent = os.path.dirname(target)
    os.makedirs(parent, mode=0o700, exist_ok=True)
    if os.path.commonpath((state.output_root, os.path.realpath(parent))) != state.output_root:
        raise ArtifactPathError("Output artifact parent escapes the private output root")
    return target


def _execution_result_snapshot() -> tuple[str | None, tuple[str, ...]]:
    context = _ACTIVE.get()
    if context is None or context.result_state is None:
        return None, ()
    state = context.result_state
    return state.structured_json, tuple(state.artifact_paths)


def _create_result_state(
    output_root: str | None,
    max_structured_json_bytes: int,
    max_artifacts: int,
    max_artifact_path_bytes: int,
) -> _ExecutionResultState | None:
    for value, label in (
        (max_structured_json_bytes, "structured JSON byte limit"),
        (max_artifacts, "artifact count limit"),
        (max_artifact_path_bytes, "artifact path byte limit"),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"Python result {label} is invalid")
    if max_structured_json_bytes == 0 and max_artifacts == 0:
        if output_root is not None or max_artifact_path_bytes != 0:
            raise ValueError("Disabled Python results must not carry output state")
        return None
    if max_artifacts == 0:
        if output_root is not None or max_artifact_path_bytes != 0:
            raise ValueError("Disabled output artifacts must use zero path state")
        normalized_output_root = None
    else:
        if output_root is None or max_artifact_path_bytes <= 0:
            raise ValueError("Output artifacts require a private output root and path limit")
        normalized_output_root = os.path.realpath(os.fspath(output_root))
        if not os.path.isdir(normalized_output_root) or os.path.islink(output_root):
            raise ValueError("Python output artifact root is unavailable")
    return _ExecutionResultState(
        output_root=normalized_output_root,
        max_structured_json_bytes=max_structured_json_bytes,
        max_artifacts=max_artifacts,
        max_artifact_path_bytes=max_artifact_path_bytes,
    )


def _require_result_state(label: str) -> _ExecutionResultState:
    context = _ACTIVE.get()
    if context is None or context.result_state is None:
        raise CapabilityUnavailableError(
            f"{label} are unavailable for this Python execution"
        )
    return context.result_state


def _artifact_relative_path(value: str, maximum_bytes: int) -> str:
    if not isinstance(value, str) or not value:
        raise ArtifactPathError("Output artifact path must be a non-empty string")
    try:
        encoded = value.encode("utf-8", "strict")
    except UnicodeError as error:
        raise ArtifactPathError("Output artifact path is not valid Unicode") from error
    if len(encoded) > maximum_bytes:
        raise ArtifactLimitError("Output artifact path exceeds the execution byte limit")
    if (
        unicodedata.normalize("NFC", value) != value
        or value.startswith("/")
        or re.match(r"^[A-Za-z]:", value)
        or "\\" in value
        or any(ord(character) < 0x20 or ord(character) == 0x7F for character in value)
    ):
        raise ArtifactPathError("Output artifact path is not a normalized relative path")
    segments = value.split("/")
    if any(not segment or segment in (".", "..") for segment in segments):
        raise ArtifactPathError("Output artifact path contains an unsafe segment")
    return value


def _require_json_value(value: Any, active: set[int], depth: int) -> None:
    if depth > 64:
        raise ValueError("Structured result nesting is too deep")
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Structured result contains a non-finite number")
        return
    if isinstance(value, (list, tuple, dict)):
        identity = id(value)
        if identity in active:
            raise ValueError("Structured result contains a cycle")
        active.add(identity)
        try:
            if isinstance(value, dict):
                if any(not isinstance(key, str) for key in value):
                    raise TypeError("Structured result object keys must be strings")
                for item in value.values():
                    _require_json_value(item, active, depth + 1)
            else:
                for item in value:
                    _require_json_value(item, active, depth + 1)
        finally:
            active.remove(identity)
        return
    raise TypeError("Structured result contains an unsupported value")


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
