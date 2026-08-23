from __future__ import annotations

import contextvars
import json
import pathlib
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = ROOT / "app" / "src" / "main" / "python"
sys.path.insert(0, str(PYTHON_SOURCE))

from autojs6 import app, clip, console, device, notice, toast  # noqa: E402
from autojs6._broker import _install_execution_broker, _reset_execution_broker  # noqa: E402
from autojs6.errors import (  # noqa: E402
    CapabilityUnavailableError,
    HostCapabilityError,
)
from autojs6_runtime.bootstrap import run_source  # noqa: E402


EXECUTION_ID = "12345678-1234-5678-9abc-def012345678"
DEVICE_INFO = {
    "schema": "autojs6-python-device-info-v1",
    "battery": {"percent": 88.5, "charging": True},
    "screen": {"on": True, "brightness": 127},
    "volume": {
        "music": {"current": 7, "max": 15},
        "notification": {"current": 4, "max": 7},
        "alarm": {"current": 5, "max": 7},
    },
}


class RecordingBroker:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, object]]] = []
        self.raw_requests: list[str] = []
        self.clipboard = ""
        self.failure: tuple[str, str] | None = None
        self.response_mutator = None

    def dispatch(self, request_json: str) -> str:
        self.raw_requests.append(request_json)
        request = json.loads(request_json)
        self.calls.append((request["capability"], request["arguments"]))
        if self.failure is not None:
            code, message = self.failure
            response: dict[str, object] = {
                "version": 1,
                "executionId": request["executionId"],
                "callId": request["callId"],
                "ok": False,
                "error": {"code": code, "message": message},
            }
        else:
            capability = request["capability"]
            arguments = request["arguments"]
            if capability == "clip.set":
                self.clipboard = arguments["text"]
                value = None
            elif capability == "clip.get":
                value = self.clipboard
            elif capability in {"app.launch", "app.launch_app", "app.open_url"}:
                value = True
            elif capability == "device.info":
                value = DEVICE_INFO
            elif capability in {
                "toast.show",
                "console.log",
                "console.warn",
                "console.error",
                "notice.show",
            }:
                value = None
            else:
                raise AssertionError(f"unexpected capability: {capability}")
            response = {
                "version": 1,
                "executionId": request["executionId"],
                "callId": request["callId"],
                "ok": True,
                "value": value,
            }
        if self.response_mutator is not None:
            self.response_mutator(response)
        return json.dumps(response, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class HostCapabilityBrokerTest(unittest.TestCase):
    def test_first_low_risk_slice_uses_monotonic_execution_bound_calls(self) -> None:
        broker = RecordingBroker()
        token = _install_execution_broker(broker, EXECUTION_ID)
        try:
            self.assertIsNone(toast("hello"))
            self.assertIsNone(clip.set("复制"))
            self.assertEqual("复制", clip.get())
            self.assertTrue(app.launch("org.example.app"))
            self.assertTrue(app.launch_app("Example"))
            self.assertTrue(app.open_url("https://example.org/path"))
            self.assertEqual(DEVICE_INFO, device.info())
            self.assertIsNone(console.log("log"))
            self.assertIsNone(console.warn("warn"))
            self.assertIsNone(console.error("error"))
            self.assertIsNone(notice("notice"))
        finally:
            _reset_execution_broker(token)

        self.assertEqual(
            [
                "toast.show",
                "clip.set",
                "clip.get",
                "app.launch",
                "app.launch_app",
                "app.open_url",
                "device.info",
                "console.log",
                "console.warn",
                "console.error",
                "notice.show",
            ],
            [capability for capability, _ in broker.calls],
        )
        decoded = [json.loads(value) for value in broker.raw_requests]
        self.assertEqual(list(range(1, 12)), [value["callId"] for value in decoded])
        self.assertTrue(all(value["executionId"] == EXECUTION_ID for value in decoded))
        self.assertEqual(
            broker.raw_requests,
            [
                json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                for value in decoded
            ],
        )
        with self.assertRaises(CapabilityUnavailableError):
            clip.get()

    def test_reset_revokes_copied_contexts_and_missing_broker_is_stable(self) -> None:
        with self.assertRaises(CapabilityUnavailableError):
            toast("outside")

        broker = RecordingBroker()
        token = _install_execution_broker(broker, EXECUTION_ID)
        copied = contextvars.copy_context()
        _reset_execution_broker(token)
        with self.assertRaises(CapabilityUnavailableError):
            copied.run(clip.get)
        self.assertEqual([], broker.calls)

    def test_host_and_protocol_failures_map_to_stable_public_errors(self) -> None:
        unavailable = RecordingBroker()
        unavailable.failure = ("CAPABILITY_UNAVAILABLE", "not granted")
        token = _install_execution_broker(unavailable, EXECUTION_ID)
        try:
            with self.assertRaises(CapabilityUnavailableError):
                clip.get()
        finally:
            _reset_execution_broker(token)

        failed = RecordingBroker()
        failed.failure = ("PERMISSION_DENIED", "notifications denied")
        token = _install_execution_broker(failed, EXECUTION_ID)
        try:
            with self.assertRaises(HostCapabilityError) as captured:
                notice("permission")
            self.assertEqual("PERMISSION_DENIED", captured.exception.code)
        finally:
            _reset_execution_broker(token)

        malformed = RecordingBroker()
        malformed.response_mutator = lambda response: response.__setitem__("callId", 999)
        token = _install_execution_broker(malformed, EXECUTION_ID)
        try:
            with self.assertRaises(HostCapabilityError) as captured:
                clip.get()
            self.assertEqual("BROKER_PROTOCOL_ERROR", captured.exception.code)
        finally:
            _reset_execution_broker(token)

    def test_live_api_argument_and_device_result_validation_is_local_and_strict(self) -> None:
        broker = RecordingBroker()
        token = _install_execution_broker(broker, EXECUTION_ID)
        try:
            with self.assertRaises(ValueError):
                notice("")
            with self.assertRaises(TypeError):
                console.log(7)  # type: ignore[arg-type]
            self.assertEqual([], broker.calls)

            broker.response_mutator = lambda response: response.__setitem__(
                "value",
                {**DEVICE_INFO, "unexpected": True},
            )
            with self.assertRaises(HostCapabilityError) as captured:
                device.info()
            self.assertEqual("BROKER_PROTOCOL_ERROR", captured.exception.code)
        finally:
            _reset_execution_broker(token)

    def test_bootstrap_installs_and_revokes_live_broker_around_user_code(self) -> None:
        broker = RecordingBroker()
        outcome = run_source(
            b"from autojs6 import app, clip, toast\n"
            b"toast('bootstrap')\n"
            b"clip.set('value')\n"
            b"print(clip.get())\n"
            b"print(app.launch('org.example.app'))\n",
            "main.py",
            [],
            4096,
            256,
            128,
            host_capability_broker_input=broker,
            execution_id=EXECUTION_ID,
        )

        self.assertEqual("completed", outcome["status"])
        self.assertEqual(b"value\nTrue\n", b"".join(chunk for _, chunk in outcome["output"]))
        self.assertEqual(
            ["toast.show", "clip.set", "clip.get", "app.launch"],
            [capability for capability, _ in broker.calls],
        )
        with self.assertRaises(CapabilityUnavailableError):
            clip.get()


if __name__ == "__main__":
    unittest.main()
