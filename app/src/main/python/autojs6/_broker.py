"""Execution-local strict JSON client for live AutoJs6 Host capabilities."""

from __future__ import annotations

import contextvars
import json
import re
import threading
import uuid
from dataclasses import dataclass, field
from typing import Any

from .errors import CapabilityUnavailableError, HostCapabilityError


_JSON_VERSION = 1
_MAX_REQUEST_BYTES = 64 * 1024
_MAX_RESPONSE_BYTES = 64 * 1024
_MAX_TEXT_BYTES = 32 * 1024
_CAPABILITY = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+$")
_SUCCESS_KEYS = frozenset(("version", "executionId", "callId", "ok", "value"))
_FAILURE_KEYS = frozenset(("version", "executionId", "callId", "ok", "error"))
_ERROR_KEYS = frozenset(("code", "message"))
_UNAVAILABLE_CODES = frozenset(("CAPABILITY_UNAVAILABLE", "BROKER_CLOSED"))


@dataclass
class _BrokerState:
    bridge: Any
    execution_id: str
    next_call_id: int = 1
    closed: bool = False
    lock: threading.Lock = field(default_factory=threading.Lock)

    def close(self) -> None:
        with self.lock:
            self.closed = True


_ACTIVE: contextvars.ContextVar[_BrokerState | None] = contextvars.ContextVar(
    "autojs6_host_capability_broker",
    default=None,
)


def _install_execution_broker(
    bridge: Any | None,
    execution_id: str | None,
) -> contextvars.Token[_BrokerState | None]:
    if bridge is None:
        if execution_id is not None:
            raise ValueError("A Python Host execution ID requires a capability broker")
        return _ACTIVE.set(None)
    if not isinstance(execution_id, str) or not execution_id:
        raise ValueError("Python Host capability execution ID is missing")
    try:
        canonical_id = str(uuid.UUID(execution_id))
    except (AttributeError, ValueError) as error:
        raise ValueError("Python Host capability execution ID is invalid") from error
    if canonical_id != execution_id:
        raise ValueError("Python Host capability execution ID is not canonical")
    if not callable(getattr(bridge, "dispatch", None)):
        raise ValueError("Python Host capability broker has no dispatch method")
    return _ACTIVE.set(_BrokerState(bridge=bridge, execution_id=execution_id))


def _reset_execution_broker(token: contextvars.Token[_BrokerState | None]) -> None:
    state = _ACTIVE.get()
    if state is not None:
        state.close()
    _ACTIVE.reset(token)


def _call(capability: str, arguments: dict[str, Any]) -> Any:
    state = _require_state()
    if not isinstance(capability, str) or _CAPABILITY.fullmatch(capability) is None:
        raise ValueError("AutoJs6 Host capability name is invalid")
    if not isinstance(arguments, dict) or any(not isinstance(key, str) for key in arguments):
        raise TypeError("AutoJs6 Host capability arguments must be a string-keyed dictionary")
    # Closing an execution takes this same lock. A call is therefore either wholly in-scope or
    # rejected before it reaches Java, including when a copied context survives in another thread.
    with state.lock:
        if state.closed:
            raise CapabilityUnavailableError(
                "AutoJs6 Host capabilities are unavailable after execution"
            )
        call_id = state.next_call_id
        state.next_call_id += 1
        document = {
            "version": _JSON_VERSION,
            "executionId": state.execution_id,
            "callId": call_id,
            "capability": capability,
            "arguments": arguments,
        }
        try:
            request_json = json.dumps(
                document,
                ensure_ascii=False,
                allow_nan=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            request_bytes = request_json.encode("utf-8", "strict")
        except (TypeError, ValueError, UnicodeError, RecursionError) as error:
            raise TypeError("AutoJs6 Host capability arguments must be strict JSON data") from error
        if not 0 < len(request_bytes) <= _MAX_REQUEST_BYTES:
            raise ValueError("AutoJs6 Host capability request exceeds the byte limit")
        try:
            response_json = state.bridge.dispatch(request_json)
        except Exception as error:
            state.closed = True
            raise CapabilityUnavailableError(
                "AutoJs6 Host capability broker became unavailable"
            ) from error
        if not isinstance(response_json, str):
            raise _protocol_error("Host capability response must be text")
        try:
            response_bytes = response_json.encode("utf-8", "strict")
        except UnicodeError as error:
            raise _protocol_error("Host capability response is not UTF-8", error)
        if not 0 < len(response_bytes) <= _MAX_RESPONSE_BYTES:
            raise _protocol_error("Host capability response exceeds the byte limit")
        return _decode_response(response_json, state.execution_id, call_id)


def _require_text(value: Any, label: str, *, allow_empty: bool = True) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{label} must be text")
    if not allow_empty and not value:
        raise ValueError(f"{label} must not be empty")
    try:
        size = len(value.encode("utf-8", "strict"))
    except UnicodeError as error:
        raise ValueError(f"{label} must be valid UTF-8 text") from error
    if size > _MAX_TEXT_BYTES:
        raise ValueError(f"{label} exceeds the {_MAX_TEXT_BYTES}-byte limit")
    return value


def _expect_none(value: Any, capability: str) -> None:
    if value is not None:
        raise _protocol_error(f"{capability} returned a non-null value")


def _expect_text(value: Any, capability: str) -> str:
    if not isinstance(value, str):
        raise _protocol_error(f"{capability} returned a non-text value")
    return value


def _expect_boolean(value: Any, capability: str) -> bool:
    if not isinstance(value, bool):
        raise _protocol_error(f"{capability} returned a non-boolean value")
    return value


def _require_state() -> _BrokerState:
    state = _ACTIVE.get()
    if state is None or state.closed:
        raise CapabilityUnavailableError(
            "AutoJs6 live Host capabilities are unavailable for this Python execution"
        )
    return state


def _decode_response(response_json: str, execution_id: str, call_id: int) -> Any:
    try:
        document = json.loads(
            response_json,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_json_constant,
        )
    except (TypeError, ValueError, RecursionError) as error:
        raise _protocol_error("Host capability response is malformed", error)
    if not isinstance(document, dict):
        raise _protocol_error("Host capability response must be an object")
    ok = document.get("ok")
    expected_keys = _SUCCESS_KEYS if ok is True else _FAILURE_KEYS if ok is False else None
    if expected_keys is None or set(document) != expected_keys:
        raise _protocol_error("Host capability response fields are invalid")
    if type(document["version"]) is not int or document["version"] != _JSON_VERSION:
        raise _protocol_error("Host capability response version is invalid")
    if document["executionId"] != execution_id:
        raise _protocol_error("Host capability response execution ID does not match")
    if type(document["callId"]) is not int or document["callId"] != call_id:
        raise _protocol_error("Host capability response call ID does not match")
    if ok:
        return document["value"]
    error = document["error"]
    if not isinstance(error, dict) or set(error) != _ERROR_KEYS:
        raise _protocol_error("Host capability error fields are invalid")
    code, message = error["code"], error["message"]
    if not isinstance(code, str) or not code or not isinstance(message, str) or not message:
        raise _protocol_error("Host capability error is invalid")
    if code in _UNAVAILABLE_CODES:
        raise CapabilityUnavailableError(message)
    raise HostCapabilityError(code, message)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> Any:
    raise ValueError(f"Invalid JSON constant: {value}")


def _protocol_error(message: str, cause: BaseException | None = None) -> HostCapabilityError:
    error = HostCapabilityError("BROKER_PROTOCOL_ERROR", message)
    if cause is not None:
        error.__cause__ = cause
    return error


__all__ = ()
