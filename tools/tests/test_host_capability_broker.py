from __future__ import annotations

import contextvars
import json
import pathlib
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = ROOT / "app" / "src" / "main" / "python"
sys.path.insert(0, str(PYTHON_SOURCE))

from autojs6 import (  # noqa: E402
    app,
    automator,
    clip,
    console,
    device,
    dialogs,
    engines,
    files,
    notice,
    selector,
    toast,
)
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
ENGINE_INFO = {
    "schema": "autojs6-python-engine-info-v1",
    "id": 17,
    "engineName": "python",
    "sourceName": "main",
    "entryPoint": "main.py",
    "project": True,
    "startedAtMillis": 123456789,
}
ENGINE_LAUNCH = {
    "schema": "autojs6-python-engine-launch-v1",
    "id": 18,
    "engineName": "org.autojs.autojs.script.JavaScriptSource.Engine",
    "sourceName": "child",
    "path": "child.js",
}
SELECTOR_NODE = {
    "id": "node-1-1",
    "parentId": None,
    "depth": 0,
    "childCount": 0,
    "text": "AutoJs6 selector smoke",
    "description": "Selector smoke description",
    "resourceId": "org.autojs.autojs6:id/selector_smoke",
    "className": "android.widget.Button",
    "packageName": "org.autojs.autojs6",
    "bounds": {"left": 1, "top": 2, "right": 101, "bottom": 202},
    "clickable": True,
    "editable": False,
    "enabled": True,
    "focused": False,
    "selected": False,
    "checkable": False,
    "checked": False,
    "scrollable": False,
    "password": False,
    "visibleToUser": True,
    "truncatedFields": [],
}
SELECTOR_SNAPSHOT = {
    "schema": selector.SNAPSHOT_SCHEMA,
    "generation": 1,
    "truncated": False,
    "nodes": [SELECTOR_NODE],
}


class RecordingBroker:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, object]]] = []
        self.raw_requests: list[str] = []
        self.clipboard = ""
        self.failure: tuple[str, str] | None = None
        self.response_mutator = None
        self.file_texts = {"seed.txt": "seed"}
        self.file_directories = {".", "nested"}
        self.dialog_results = {
            "dialogs.alert": None,
            "dialogs.confirm": True,
            "dialogs.prompt": "typed value",
            "dialogs.select": 1,
        }

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
            elif capability == "files.read_text":
                value = self.file_texts[arguments["path"]]
            elif capability == "files.write_text":
                self.file_texts[arguments["path"]] = arguments["text"]
                value = None
            elif capability == "files.exists":
                value = (
                    arguments["path"] in self.file_texts
                    or arguments["path"] in self.file_directories
                )
            elif capability == "files.is_file":
                value = arguments["path"] in self.file_texts
            elif capability == "files.is_dir":
                value = arguments["path"] in self.file_directories
            elif capability == "files.list":
                value = sorted(
                    [*self.file_texts, *(entry for entry in self.file_directories if entry != ".")]
                )
            elif capability in self.dialog_results:
                value = self.dialog_results[capability]
            elif capability == "engines.current":
                value = ENGINE_INFO
            elif capability == "engines.run":
                value = {**ENGINE_LAUNCH, "path": arguments["path"]}
            elif capability in {
                "automator.click",
                "automator.long_click",
                "automator.press",
                "automator.swipe",
                "automator.back",
                "automator.home",
            }:
                value = True
            elif capability == "selector.snapshot":
                value = SELECTOR_SNAPSHOT
            elif capability == "selector.find":
                value = SELECTOR_NODE
            elif capability in {"selector.click", "selector.set_text"}:
                value = True
            elif capability in {
                "toast.show",
                "console.log",
                "console.warn",
                "console.error",
                "notice.show",
                "engines.stop_self",
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

    def test_host_files_are_execution_relative_bounded_and_strict(self) -> None:
        broker = RecordingBroker()
        token = _install_execution_broker(broker, EXECUTION_ID)
        try:
            self.assertEqual("seed", files.read_text("seed.txt"))
            self.assertIsNone(files.write_text("written.txt", "写入"))
            self.assertTrue(files.exists("written.txt"))
            self.assertTrue(files.is_file("written.txt"))
            self.assertTrue(files.is_dir("."))
            self.assertFalse(files.exists("missing.txt"))
            self.assertEqual(
                ["nested", "seed.txt", "written.txt"],
                files.list(),
            )
            self.assertEqual("写入", broker.file_texts["written.txt"])

            call_count = len(broker.calls)
            for unsafe in (
                "",
                "../outside",
                "/absolute",
                "C:/absolute",
                "C:relative",
                "a\\b",
                "a//b",
                "entry\u0085.txt",
            ):
                with self.subTest(unsafe=unsafe):
                    with self.assertRaises(ValueError):
                        files.exists(unsafe)
            with self.assertRaises(ValueError):
                files.write_text("too-large.txt", "x" * (files.MAX_TEXT_BYTES + 1))
            self.assertEqual(call_count, len(broker.calls))
        finally:
            _reset_execution_broker(token)

    def test_host_files_map_host_failures_and_reject_malformed_lists(self) -> None:
        broker = RecordingBroker()
        broker.failure = ("PATH_NOT_FOUND", "missing")
        token = _install_execution_broker(broker, EXECUTION_ID)
        try:
            with self.assertRaises(HostCapabilityError) as captured:
                files.read_text("missing.txt")
            self.assertEqual("PATH_NOT_FOUND", captured.exception.code)
        finally:
            _reset_execution_broker(token)

    def test_foreground_dialogs_use_typed_bounded_requests_and_results(self) -> None:
        broker = RecordingBroker()
        token = _install_execution_broker(broker, EXECUTION_ID)
        try:
            self.assertIsNone(dialogs.alert("Alert text"))
            self.assertTrue(dialogs.confirm("Confirm text", title="Question"))
            self.assertEqual(
                "typed value",
                dialogs.prompt("Prompt text", default="seed", title="Input"),
            )
            self.assertEqual(1, dialogs.select(("first", "second"), title="Choose"))
        finally:
            _reset_execution_broker(token)

        self.assertEqual(
            [
                ("dialogs.alert", {"title": dialogs.DEFAULT_TITLE, "text": "Alert text"}),
                ("dialogs.confirm", {"title": "Question", "text": "Confirm text"}),
                (
                    "dialogs.prompt",
                    {"title": "Input", "text": "Prompt text", "default": "seed"},
                ),
                ("dialogs.select", {"title": "Choose", "items": ["first", "second"]}),
            ],
            broker.calls,
        )

        cancelled = RecordingBroker()
        cancelled.dialog_results.update(
            {
                "dialogs.confirm": False,
                "dialogs.prompt": None,
                "dialogs.select": None,
            }
        )
        token = _install_execution_broker(cancelled, EXECUTION_ID)
        try:
            self.assertFalse(dialogs.confirm("cancel"))
            self.assertIsNone(dialogs.prompt("cancel"))
            self.assertIsNone(dialogs.select(["cancel"]))
        finally:
            _reset_execution_broker(token)

    def test_dialog_validation_and_foreground_authorization_fail_closed(self) -> None:
        broker = RecordingBroker()
        token = _install_execution_broker(broker, EXECUTION_ID)
        try:
            invalid_calls = (
                lambda: dialogs.alert("text", title=""),
                lambda: dialogs.alert("x" * (dialogs.MAX_TEXT_BYTES + 1)),
                lambda: dialogs.prompt("text", default="x" * (dialogs.MAX_PROMPT_REPLY_BYTES + 1)),
                lambda: dialogs.select("not-a-sequence-of-items"),
                lambda: dialogs.select([]),
                lambda: dialogs.select([""]),
                lambda: dialogs.select(["item"] * (dialogs.MAX_ITEMS + 1)),
            )
            for invalid in invalid_calls:
                with self.subTest(invalid=invalid), self.assertRaises((TypeError, ValueError)):
                    invalid()
            self.assertEqual([], broker.calls)
        finally:
            _reset_execution_broker(token)

        denied = RecordingBroker()
        denied.failure = (
            "INTERACTIVE_NOT_ALLOWED",
            "Host dialog requires a foreground user-authorized execution",
        )
        token = _install_execution_broker(denied, EXECUTION_ID)
        try:
            with self.assertRaises(HostCapabilityError) as captured:
                dialogs.alert("background")
            self.assertEqual("INTERACTIVE_NOT_ALLOWED", captured.exception.code)
        finally:
            _reset_execution_broker(token)

    def test_dialog_facade_rejects_malformed_host_results(self) -> None:
        malformed_prompt = RecordingBroker()
        malformed_prompt.dialog_results["dialogs.prompt"] = 7
        token = _install_execution_broker(malformed_prompt, EXECUTION_ID)
        try:
            with self.assertRaises(HostCapabilityError) as captured:
                dialogs.prompt("prompt")
            self.assertEqual("BROKER_PROTOCOL_ERROR", captured.exception.code)
        finally:
            _reset_execution_broker(token)

    def test_automator_uses_bounded_typed_actions_and_boolean_results(self) -> None:
        broker = RecordingBroker()
        token = _install_execution_broker(broker, EXECUTION_ID)
        try:
            self.assertTrue(automator.click(10, 20))
            self.assertTrue(automator.long_click(11, 21))
            self.assertTrue(automator.press(12, 22, 75))
            self.assertTrue(automator.swipe(1, 2, 101, 202, 350))
            self.assertTrue(automator.back())
            self.assertTrue(automator.home())
        finally:
            _reset_execution_broker(token)

        self.assertEqual(
            [
                ("automator.click", {"x": 10, "y": 20}),
                ("automator.long_click", {"x": 11, "y": 21}),
                (
                    "automator.press",
                    {"x": 12, "y": 22, "durationMillis": 75},
                ),
                (
                    "automator.swipe",
                    {
                        "x1": 1,
                        "y1": 2,
                        "x2": 101,
                        "y2": 202,
                        "durationMillis": 350,
                    },
                ),
                ("automator.back", {}),
                ("automator.home", {}),
            ],
            broker.calls,
        )

    def test_automator_rejects_invalid_values_before_dispatch(self) -> None:
        broker = RecordingBroker()
        token = _install_execution_broker(broker, EXECUTION_ID)
        try:
            invalid_calls = (
                lambda: automator.click(True, 0),
                lambda: automator.click(0.5, 0),
                lambda: automator.click(-1, 0),
                lambda: automator.click(automator.MAX_COORDINATE + 1, 0),
                lambda: automator.press(0, 0, False),
                lambda: automator.press(0, 0, 0),
                lambda: automator.swipe(0, 0, 1, 1, automator.MAX_DURATION_MILLIS + 1),
            )
            for invalid in invalid_calls:
                with self.subTest(invalid=invalid), self.assertRaises((TypeError, ValueError)):
                    invalid()
            self.assertEqual([], broker.calls)
        finally:
            _reset_execution_broker(token)

    def test_automator_maps_unavailable_accessibility_and_rejects_malformed_results(self) -> None:
        unavailable = RecordingBroker()
        unavailable.failure = (
            "ACCESSIBILITY_UNAVAILABLE",
            "AutoJs6 accessibility service is unavailable",
        )
        token = _install_execution_broker(unavailable, EXECUTION_ID)
        try:
            with self.assertRaises(CapabilityUnavailableError):
                automator.home()
        finally:
            _reset_execution_broker(token)

        malformed = RecordingBroker()
        malformed.response_mutator = lambda response: response.__setitem__("value", "true")
        token = _install_execution_broker(malformed, EXECUTION_ID)
        try:
            with self.assertRaises(HostCapabilityError) as captured:
                automator.back()
            self.assertEqual("BROKER_PROTOCOL_ERROR", captured.exception.code)
        finally:
            _reset_execution_broker(token)

        malformed_selection = RecordingBroker()
        malformed_selection.dialog_results["dialogs.select"] = True
        token = _install_execution_broker(malformed_selection, EXECUTION_ID)
        try:
            with self.assertRaises(HostCapabilityError) as captured:
                dialogs.select(["only"])
            self.assertEqual("BROKER_PROTOCOL_ERROR", captured.exception.code)
        finally:
            _reset_execution_broker(token)

        malformed = RecordingBroker()
        malformed.response_mutator = lambda response: response.__setitem__(
            "value",
            ["duplicate.txt", "duplicate.txt"],
        )
        token = _install_execution_broker(malformed, EXECUTION_ID)
        try:
            with self.assertRaises(HostCapabilityError) as captured:
                files.list()
            self.assertEqual("BROKER_PROTOCOL_ERROR", captured.exception.code)
        finally:
            _reset_execution_broker(token)

    def test_selector_uses_bounded_snapshots_queries_and_explicit_node_actions(self) -> None:
        broker = RecordingBroker()
        token = _install_execution_broker(broker, EXECUTION_ID)
        try:
            self.assertEqual(SELECTOR_SNAPSHOT, selector.snapshot(max_nodes=2, max_depth=3))
            node = selector.find(
                text_contains="smoke",
                description="Selector smoke description",
                resource_id="org.autojs.autojs6:id/selector_smoke",
                class_name="android.widget.Button",
                clickable=True,
                editable=False,
                enabled=True,
                scrollable=False,
                max_nodes=12,
                max_depth=4,
            )
            self.assertEqual(SELECTOR_NODE, node)
            self.assertTrue(selector.click(node))
            self.assertTrue(selector.click(SELECTOR_NODE["id"]))
            self.assertTrue(selector.set_text(node, "updated"))
        finally:
            _reset_execution_broker(token)

        self.assertEqual(
            [
                ("selector.snapshot", {"maxNodes": 2, "maxDepth": 3}),
                (
                    "selector.find",
                    {
                        "query": {
                            "textContains": "smoke",
                            "description": "Selector smoke description",
                            "resourceId": "org.autojs.autojs6:id/selector_smoke",
                            "className": "android.widget.Button",
                            "clickable": True,
                            "editable": False,
                            "enabled": True,
                            "scrollable": False,
                        },
                        "maxNodes": 12,
                        "maxDepth": 4,
                    },
                ),
                ("selector.click", {"nodeId": "node-1-1"}),
                ("selector.click", {"nodeId": "node-1-1"}),
                ("selector.set_text", {"nodeId": "node-1-1", "text": "updated"}),
            ],
            broker.calls,
        )

    def test_selector_rejects_invalid_inputs_before_dispatch(self) -> None:
        broker = RecordingBroker()
        token = _install_execution_broker(broker, EXECUTION_ID)
        try:
            invalid_calls = (
                lambda: selector.snapshot(max_nodes=True),
                lambda: selector.snapshot(max_nodes=0),
                lambda: selector.snapshot(max_nodes=selector.MAX_SNAPSHOT_NODES + 1),
                lambda: selector.snapshot(max_depth=-1),
                lambda: selector.snapshot(max_depth=selector.MAX_DEPTH + 1),
                lambda: selector.find(),
                lambda: selector.find(text=""),
                lambda: selector.find(text="x" * (selector.MAX_QUERY_TEXT_BYTES + 1)),
                lambda: selector.find(clickable=1),
                lambda: selector.find(text="target", max_nodes=False),
                lambda: selector.find(text="target", max_nodes=selector.MAX_FIND_NODES + 1),
                lambda: selector.click(7),
                lambda: selector.click({}),
                lambda: selector.click("raw-handle"),
                lambda: selector.set_text("node-1-1", 7),
                lambda: selector.set_text(
                    "node-1-1",
                    "x" * (selector.MAX_SET_TEXT_BYTES + 1),
                ),
            )
            for invalid in invalid_calls:
                with self.subTest(invalid=invalid), self.assertRaises((TypeError, ValueError)):
                    invalid()
            self.assertEqual([], broker.calls)
        finally:
            _reset_execution_broker(token)

    def test_selector_maps_lifecycle_failures_and_rejects_malformed_results(self) -> None:
        failure_cases = (
            (
                "ACCESSIBILITY_UNAVAILABLE",
                "AutoJs6 accessibility service is unavailable",
                CapabilityUnavailableError,
                lambda: selector.snapshot(),
            ),
            (
                "STALE_NODE",
                "Host selector node is stale or no longer retained",
                HostCapabilityError,
                lambda: selector.click("node-1-1"),
            ),
            (
                "SELECTOR_SCAN_LIMIT_EXCEEDED",
                "Host selector scan reached its node or depth limit",
                HostCapabilityError,
                lambda: selector.find(text="missing"),
            ),
        )
        for code, message, error_type, action in failure_cases:
            broker = RecordingBroker()
            broker.failure = (code, message)
            token = _install_execution_broker(broker, EXECUTION_ID)
            try:
                with self.subTest(code=code), self.assertRaises(error_type) as captured:
                    action()
                if isinstance(captured.exception, HostCapabilityError):
                    self.assertEqual(code, captured.exception.code)
            finally:
                _reset_execution_broker(token)

        malformed_snapshots = (
            {**SELECTOR_SNAPSHOT, "schema": "wrong"},
            {**SELECTOR_SNAPSHOT, "generation": True},
            {**SELECTOR_SNAPSHOT, "nodes": []},
            {
                **SELECTOR_SNAPSHOT,
                "nodes": [{**SELECTOR_NODE, "clickable": "true"}],
            },
            {
                **SELECTOR_SNAPSHOT,
                "nodes": [
                    {
                        **SELECTOR_NODE,
                        "truncatedFields": ["text"],
                    }
                ],
            },
        )
        for malformed_value in malformed_snapshots:
            broker = RecordingBroker()
            broker.response_mutator = lambda response, value=malformed_value: response.__setitem__(
                "value", value
            )
            token = _install_execution_broker(broker, EXECUTION_ID)
            try:
                with self.assertRaises(HostCapabilityError) as captured:
                    selector.snapshot()
                self.assertEqual("BROKER_PROTOCOL_ERROR", captured.exception.code)
            finally:
                _reset_execution_broker(token)

        malformed_find = RecordingBroker()
        malformed_find.response_mutator = lambda response: response.__setitem__("value", "node")
        token = _install_execution_broker(malformed_find, EXECUTION_ID)
        try:
            with self.assertRaises(HostCapabilityError) as captured:
                selector.find(text="target")
            self.assertEqual("BROKER_PROTOCOL_ERROR", captured.exception.code)
        finally:
            _reset_execution_broker(token)

    def test_engines_use_typed_identity_scoped_launch_and_nonreturning_self_stop(self) -> None:
        broker = RecordingBroker()
        token = _install_execution_broker(broker, EXECUTION_ID)
        try:
            self.assertEqual(ENGINE_INFO, engines.current())
            self.assertEqual(ENGINE_LAUNCH, engines.run("child.js"))
            with self.assertRaises(SystemExit) as stopped:
                engines.stop_self()
            self.assertEqual(0, stopped.exception.code)
        finally:
            _reset_execution_broker(token)

        self.assertEqual(
            [
                ("engines.current", {}),
                ("engines.run", {"path": "child.js"}),
                ("engines.stop_self", {}),
            ],
            broker.calls,
        )

    def test_engines_validate_paths_and_map_nested_python_rejection(self) -> None:
        broker = RecordingBroker()
        token = _install_execution_broker(broker, EXECUTION_ID)
        try:
            for unsafe in ("", "../outside.js", "/absolute.js", "C:/absolute.js", "a\\b.js"):
                with self.subTest(unsafe=unsafe), self.assertRaises(ValueError):
                    engines.run(unsafe)
            self.assertEqual([], broker.calls)
        finally:
            _reset_execution_broker(token)

        denied = RecordingBroker()
        denied.failure = (
            "NESTED_PYTHON_NOT_ALLOWED",
            "nested Python is unavailable",
        )
        token = _install_execution_broker(denied, EXECUTION_ID)
        try:
            with self.assertRaises(HostCapabilityError) as captured:
                engines.run("child.py")
            self.assertEqual("NESTED_PYTHON_NOT_ALLOWED", captured.exception.code)
        finally:
            _reset_execution_broker(token)

    def test_engines_reject_malformed_host_identity_and_launch_results(self) -> None:
        malformed = RecordingBroker()
        malformed.response_mutator = lambda response: response.__setitem__(
            "value",
            {**ENGINE_INFO, "engineName": "javascript"},
        )
        token = _install_execution_broker(malformed, EXECUTION_ID)
        try:
            with self.assertRaises(HostCapabilityError) as captured:
                engines.current()
            self.assertEqual("BROKER_PROTOCOL_ERROR", captured.exception.code)
        finally:
            _reset_execution_broker(token)

        malformed = RecordingBroker()
        malformed.response_mutator = lambda response: response.__setitem__(
            "value",
            {**ENGINE_LAUNCH, "path": "different.js"},
        )
        token = _install_execution_broker(malformed, EXECUTION_ID)
        try:
            with self.assertRaises(HostCapabilityError) as captured:
                engines.run("child.js")
            self.assertEqual("BROKER_PROTOCOL_ERROR", captured.exception.code)
        finally:
            _reset_execution_broker(token)

    def test_bootstrap_stop_self_never_executes_following_user_code(self) -> None:
        broker = RecordingBroker()
        outcome = run_source(
            b"from autojs6 import engines\n"
            b"print('before', flush=True)\n"
            b"engines.stop_self()\n"
            b"print('after', flush=True)\n",
            "main.py",
            [],
            4096,
            256,
            128,
            host_capability_broker_input=broker,
            execution_id=EXECUTION_ID,
        )

        self.assertEqual("completed", outcome["status"])
        self.assertEqual(0, outcome["exit_code"])
        self.assertEqual(b"before\n", b"".join(chunk for _, chunk in outcome["output"]))
        self.assertEqual([("engines.stop_self", {})], broker.calls)

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
