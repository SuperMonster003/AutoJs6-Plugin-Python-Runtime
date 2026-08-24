from __future__ import annotations

import contextvars
import base64
import hashlib
import json
import pathlib
import sys
import tempfile
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
    images,
    notice,
    ocr,
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
PNG_BYTES = b"\x89PNG\r\n\x1a\n" + bytes(
    index % 251 for index in range(images.MAX_CHUNK_BYTES + 3)
)
JPEG_BYTES = b"\xff\xd8" + bytes(index % 251 for index in range(257)) + b"\xff\xd9"


class RecordingBroker:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, object]]] = []
        self.raw_requests: list[str] = []
        self.clipboard = ""
        self.failure: tuple[str, str] | None = None
        self.capability_failures: dict[str, tuple[str, str]] = {}
        self.capability_mutators: dict[str, object] = {}
        self.response_mutator = None
        self.file_texts = {"seed.txt": "seed"}
        self.file_directories = {".", "nested"}
        self.dialog_results = {
            "dialogs.alert": None,
            "dialogs.confirm": True,
            "dialogs.prompt": "typed value",
            "dialogs.select": 1,
        }
        self.image_generation = 0
        self.image_bytes_override: bytes | None = None
        self.retained_image: tuple[str, bytes, str] | None = None
        self.image_releases: list[str] = []
        self.color_match: tuple[int, int] | None = (17, 29)
        self.template_generation = 0
        self.pending_template: dict[str, object] | None = None
        self.retained_template: tuple[str, bytes, str, int, int] | None = None
        self.uploaded_templates: list[tuple[str, bytes, str]] = []
        self.template_releases: list[str] = []
        self.template_dimensions = (4, 3)
        self.image_match: tuple[int, int] | None = (17, 29)
        self.ocr_lines = ["AutoJs6", "中文 OCR"]

    def dispatch(self, request_json: str) -> str:
        self.raw_requests.append(request_json)
        request = json.loads(request_json)
        capability = request["capability"]
        arguments = request["arguments"]
        self.calls.append((capability, arguments))
        failure = self.capability_failures.get(capability, self.failure)
        if failure is not None:
            code, message = failure
            response: dict[str, object] = {
                "version": 1,
                "executionId": request["executionId"],
                "callId": request["callId"],
                "ok": False,
                "error": {"code": code, "message": message},
            }
        else:
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
            elif capability == "images.capture_screen":
                self.image_generation += 1
                image_id = f"image-{self.image_generation}"
                image_format = arguments["format"]
                image_bytes = self.image_bytes_override or (
                    PNG_BYTES if image_format == "png" else JPEG_BYTES
                )
                self.retained_image = (image_id, image_bytes, image_format)
                value = {
                    "schema": images.IMAGE_SCHEMA,
                    "id": image_id,
                    "format": image_format,
                    "width": 1080,
                    "height": 2400,
                    "byteLength": len(image_bytes),
                    "sha256": hashlib.sha256(image_bytes).hexdigest(),
                }
            elif capability == "images.read_chunk":
                retained = self.retained_image
                if retained is None or arguments["imageId"] != retained[0]:
                    raise AssertionError("unexpected stale image read")
                image_id, image_bytes, _ = retained
                offset = arguments["offset"]
                chunk = image_bytes[offset : offset + images.MAX_CHUNK_BYTES]
                next_offset = offset + len(chunk)
                value = {
                    "schema": images.CHUNK_SCHEMA,
                    "imageId": image_id,
                    "offset": offset,
                    "data": base64.b64encode(chunk).decode("ascii"),
                    "nextOffset": next_offset,
                    "eof": next_offset == len(image_bytes),
                }
            elif capability == "images.release":
                retained = self.retained_image
                if retained is None or arguments["imageId"] != retained[0]:
                    raise AssertionError("unexpected stale image release")
                self.image_releases.append(arguments["imageId"])
                self.retained_image = None
                value = None
            elif capability == "images.find_color":
                if self.color_match is None:
                    value = {
                        "schema": images.COLOR_MATCH_SCHEMA,
                        "found": False,
                        "x": -1,
                        "y": -1,
                    }
                else:
                    value = {
                        "schema": images.COLOR_MATCH_SCHEMA,
                        "found": True,
                        "x": self.color_match[0],
                        "y": self.color_match[1],
                    }
            elif capability == "images.begin_template":
                self.template_generation += 1
                template_id = f"template-{self.template_generation}"
                self.pending_template = {
                    "id": template_id,
                    "format": arguments["format"],
                    "byteLength": arguments["byteLength"],
                    "sha256": arguments["sha256"],
                    "payload": bytearray(),
                }
                self.retained_template = None
                value = {
                    "schema": images.TEMPLATE_SCHEMA,
                    "id": template_id,
                    "format": arguments["format"],
                    "byteLength": arguments["byteLength"],
                }
            elif capability == "images.write_template_chunk":
                pending = self.pending_template
                if pending is None or arguments["templateId"] != pending["id"]:
                    raise AssertionError("unexpected stale template upload")
                payload = pending["payload"]
                if not isinstance(payload, bytearray):
                    raise AssertionError("unexpected template upload buffer")
                if arguments["offset"] != len(payload):
                    raise AssertionError("unexpected template upload offset")
                decoded = base64.b64decode(arguments["data"], validate=True)
                if base64.b64encode(decoded).decode("ascii") != arguments["data"]:
                    raise AssertionError("unexpected non-canonical template chunk")
                payload.extend(decoded)
                byte_length = pending["byteLength"]
                if type(byte_length) is not int or len(payload) > byte_length:
                    raise AssertionError("unexpected template upload length")
                complete = len(payload) == byte_length
                width, height = self.template_dimensions if complete else (0, 0)
                if complete:
                    uploaded = bytes(payload)
                    if hashlib.sha256(uploaded).hexdigest() != pending["sha256"]:
                        raise AssertionError("unexpected template upload digest")
                    retained = (
                        str(pending["id"]),
                        uploaded,
                        str(pending["format"]),
                        width,
                        height,
                    )
                    self.retained_template = retained
                    self.uploaded_templates.append((retained[0], retained[1], retained[2]))
                    self.pending_template = None
                value = {
                    "schema": images.TEMPLATE_CHUNK_SCHEMA,
                    "templateId": arguments["templateId"],
                    "offset": arguments["offset"],
                    "nextOffset": len(payload),
                    "complete": complete,
                    "width": width,
                    "height": height,
                }
            elif capability == "images.find_image":
                retained = self.retained_template
                if retained is None or arguments["templateId"] != retained[0]:
                    raise AssertionError("unexpected stale template search")
                if self.image_match is None:
                    value = {
                        "schema": images.IMAGE_MATCH_SCHEMA,
                        "found": False,
                        "x": -1,
                        "y": -1,
                    }
                else:
                    value = {
                        "schema": images.IMAGE_MATCH_SCHEMA,
                        "found": True,
                        "x": self.image_match[0],
                        "y": self.image_match[1],
                    }
            elif capability == "ocr.recognize":
                retained = self.retained_template
                if retained is None or arguments["templateId"] != retained[0]:
                    raise AssertionError("unexpected stale OCR image")
                value = list(self.ocr_lines)
            elif capability == "images.release_template":
                template_id = arguments["templateId"]
                pending_id = None if self.pending_template is None else self.pending_template["id"]
                retained_id = None if self.retained_template is None else self.retained_template[0]
                if template_id not in (pending_id, retained_id):
                    raise AssertionError("unexpected stale template release")
                self.template_releases.append(template_id)
                self.pending_template = None
                self.retained_template = None
                value = None
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
        capability_mutator = self.capability_mutators.get(capability)
        if capability_mutator is not None:
            capability_mutator(response)
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

    def test_images_capture_validates_and_releases_ordered_screen_bytes(self) -> None:
        broker = RecordingBroker()
        token = _install_execution_broker(broker, EXECUTION_ID)
        try:
            self.assertEqual(PNG_BYTES, images.capture_screen())
        finally:
            _reset_execution_broker(token)

        self.assertEqual(
            [
                ("images.capture_screen", {"format": "png", "quality": 100}),
                ("images.read_chunk", {"imageId": "image-1", "offset": 0}),
                (
                    "images.read_chunk",
                    {"imageId": "image-1", "offset": images.MAX_CHUNK_BYTES},
                ),
                ("images.release", {"imageId": "image-1"}),
            ],
            broker.calls,
        )
        self.assertEqual(["image-1"], broker.image_releases)
        self.assertIsNone(broker.retained_image)

        jpeg = RecordingBroker()
        token = _install_execution_broker(jpeg, EXECUTION_ID)
        try:
            self.assertEqual(
                JPEG_BYTES,
                images.capture_screen(format="jpeg", quality=75),
            )
        finally:
            _reset_execution_broker(token)
        self.assertEqual(
            ("images.capture_screen", {"format": "jpeg", "quality": 75}),
            jpeg.calls[0],
        )
        self.assertEqual("images.release", jpeg.calls[-1][0])

    def test_images_capture_atomically_writes_an_output_artifact_after_release(self) -> None:
        broker = RecordingBroker()
        with tempfile.TemporaryDirectory() as directory:
            outcome = run_source(
                b"from autojs6 import images\n"
                b"images.capture_screen(path='screens/current.png')\n",
                "main.py",
                [],
                4096,
                256,
                128,
                output_artifact_root=directory,
                max_output_artifacts=1,
                max_output_artifact_path_bytes=128,
                host_capability_broker_input=broker,
                execution_id=EXECUTION_ID,
            )
            target = pathlib.Path(directory, "screens", "current.png")
            self.assertEqual(PNG_BYTES, target.read_bytes())
            self.assertEqual([], list(pathlib.Path(directory).rglob(".autojs6-capture-*")))

        self.assertEqual("completed", outcome["status"])
        self.assertEqual(("screens/current.png",), outcome["artifact_paths"])
        self.assertEqual("images.release", broker.calls[-1][0])
        self.assertIsNone(broker.retained_image)

    def test_images_reject_invalid_options_before_dispatch(self) -> None:
        broker = RecordingBroker()
        token = _install_execution_broker(broker, EXECUTION_ID)
        try:
            invalid_calls = (
                lambda: images.capture_screen(format=7),
                lambda: images.capture_screen(format="PNG"),
                lambda: images.capture_screen(format="jpg"),
                lambda: images.capture_screen(quality=True),
                lambda: images.capture_screen(quality=0),
                lambda: images.capture_screen(quality=images.MAX_QUALITY + 1),
                lambda: images.capture_screen(path=7),
            )
            for invalid in invalid_calls:
                with self.subTest(invalid=invalid), self.assertRaises((TypeError, ValueError)):
                    invalid()
            self.assertEqual([], broker.calls)
        finally:
            _reset_execution_broker(token)

    def test_images_find_color_uses_bounded_rgb_region_and_threshold(self) -> None:
        broker = RecordingBroker()
        token = _install_execution_broker(broker, EXECUTION_ID)
        try:
            self.assertEqual(
                (17, 29),
                images.find_color(
                    "#123456",
                    region=(10, 20, 100, 200),
                    threshold=2,
                ),
            )
            broker.color_match = None
            self.assertIsNone(images.find_color(0xABCDEF, region=None))
        finally:
            _reset_execution_broker(token)

        self.assertEqual(
            [
                (
                    "images.find_color",
                    {
                        "color": 0x123456,
                        "threshold": 2,
                        "region": {"x": 10, "y": 20, "width": 100, "height": 200},
                    },
                ),
                (
                    "images.find_color",
                    {"color": 0xABCDEF, "threshold": 0, "region": None},
                ),
            ],
            broker.calls,
        )

    def test_images_find_color_rejects_invalid_inputs_before_dispatch(self) -> None:
        broker = RecordingBroker()
        token = _install_execution_broker(broker, EXECUTION_ID)
        try:
            invalid_calls = (
                lambda: images.find_color(True),
                lambda: images.find_color(-1),
                lambda: images.find_color(images.MAX_COLOR + 1),
                lambda: images.find_color("123456"),
                lambda: images.find_color("#12345G"),
                lambda: images.find_color("#1234567"),
                lambda: images.find_color(0, threshold=True),
                lambda: images.find_color(0, threshold=-1),
                lambda: images.find_color(0, threshold=images.MAX_COLOR_THRESHOLD + 1),
                lambda: images.find_color(0, region=7),
                lambda: images.find_color(0, region=(0, 0, 1)),
                lambda: images.find_color(0, region=(True, 0, 1, 1)),
                lambda: images.find_color(0, region=(-1, 0, 1, 1)),
                lambda: images.find_color(0, region=(0, 0, 0, 1)),
                lambda: images.find_color(0, region=(0, 0, images.MAX_DIMENSION + 1, 1)),
                lambda: images.find_color(
                    0,
                    region=(images.MAX_DIMENSION - 1, 0, 2, 1),
                ),
            )
            for invalid in invalid_calls:
                with self.subTest(invalid=invalid), self.assertRaises((TypeError, ValueError)):
                    invalid()
            self.assertEqual([], broker.calls)
        finally:
            _reset_execution_broker(token)

    def test_images_find_color_maps_capture_failures_and_rejects_malformed_results(self) -> None:
        for code, error_type in (
            ("ACCESSIBILITY_UNAVAILABLE", CapabilityUnavailableError),
            ("SCREEN_CAPTURE_UNAVAILABLE", CapabilityUnavailableError),
            ("SCREEN_CAPTURE_FAILED", HostCapabilityError),
            ("RESULT_LIMIT_EXCEEDED", HostCapabilityError),
        ):
            broker = RecordingBroker()
            broker.failure = (code, "screen color failure")
            token = _install_execution_broker(broker, EXECUTION_ID)
            try:
                with self.subTest(code=code), self.assertRaises(error_type) as captured:
                    images.find_color(0x123456)
                if isinstance(captured.exception, HostCapabilityError):
                    self.assertEqual(code, captured.exception.code)
            finally:
                _reset_execution_broker(token)

        malformed_values = (
            "not-an-object",
            {
                "schema": "wrong",
                "found": True,
                "x": 17,
                "y": 29,
            },
            {
                "schema": images.COLOR_MATCH_SCHEMA,
                "found": 1,
                "x": 17,
                "y": 29,
            },
            {
                "schema": images.COLOR_MATCH_SCHEMA,
                "found": False,
                "x": 0,
                "y": 0,
            },
            {
                "schema": images.COLOR_MATCH_SCHEMA,
                "found": True,
                "x": True,
                "y": 29,
            },
            {
                "schema": images.COLOR_MATCH_SCHEMA,
                "found": True,
                "x": images.MAX_DIMENSION,
                "y": 29,
            },
            {
                "schema": images.COLOR_MATCH_SCHEMA,
                "found": True,
                "x": 0,
                "y": 0,
            },
            {
                "schema": images.COLOR_MATCH_SCHEMA,
                "found": True,
                "x": 10,
                "y": 20,
                "unexpected": True,
            },
        )
        for malformed in malformed_values:
            broker = RecordingBroker()
            broker.response_mutator = lambda response, value=malformed: response.__setitem__(
                "value", value
            )
            token = _install_execution_broker(broker, EXECUTION_ID)
            try:
                with self.subTest(malformed=malformed), self.assertRaises(
                    HostCapabilityError
                ) as captured:
                    images.find_color(0x123456, region=(10, 20, 2, 2))
                self.assertEqual("BROKER_PROTOCOL_ERROR", captured.exception.code)
            finally:
                _reset_execution_broker(token)

    def test_images_find_image_uploads_bounded_templates_and_always_releases(self) -> None:
        broker = RecordingBroker()
        token = _install_execution_broker(broker, EXECUTION_ID)
        try:
            self.assertEqual(
                (17, 29),
                images.find_image(
                    memoryview(PNG_BYTES),
                    region=(10, 20, 100, 200),
                    threshold=2,
                ),
            )
            broker.image_match = None
            self.assertIsNone(images.find_image(bytearray(JPEG_BYTES)))
        finally:
            _reset_execution_broker(token)

        self.assertEqual(
            [
                "images.begin_template",
                "images.write_template_chunk",
                "images.write_template_chunk",
                "images.find_image",
                "images.release_template",
                "images.begin_template",
                "images.write_template_chunk",
                "images.find_image",
                "images.release_template",
            ],
            [capability for capability, _ in broker.calls],
        )
        self.assertEqual(
            {
                "format": "png",
                "byteLength": len(PNG_BYTES),
                "sha256": hashlib.sha256(PNG_BYTES).hexdigest(),
            },
            broker.calls[0][1],
        )
        uploaded_chunks = [
            base64.b64decode(arguments["data"], validate=True)
            for capability, arguments in broker.calls[1:3]
            if capability == "images.write_template_chunk"
        ]
        self.assertEqual(PNG_BYTES, b"".join(uploaded_chunks))
        self.assertEqual(images.MAX_TEMPLATE_CHUNK_BYTES, len(uploaded_chunks[0]))
        self.assertEqual(
            {
                "templateId": "template-1",
                "threshold": 2,
                "region": {"x": 10, "y": 20, "width": 100, "height": 200},
            },
            broker.calls[3][1],
        )
        self.assertEqual(
            [
                ("template-1", PNG_BYTES, "png"),
                ("template-2", JPEG_BYTES, "jpeg"),
            ],
            broker.uploaded_templates,
        )
        self.assertEqual(["template-1", "template-2"], broker.template_releases)
        self.assertIsNone(broker.pending_template)
        self.assertIsNone(broker.retained_template)

    def test_images_find_image_rejects_invalid_inputs_before_dispatch(self) -> None:
        broker = RecordingBroker()
        token = _install_execution_broker(broker, EXECUTION_ID)
        invalid_payload = bytearray(b"not-an-image")
        try:
            invalid_calls = (
                lambda: images.find_image("png"),
                lambda: images.find_image([]),
                lambda: images.find_image(b""),
                lambda: images.find_image(
                    b"\x89PNG\r\n\x1a\n" + b"x" * images.MAX_TEMPLATE_BYTES
                ),
                lambda: images.find_image(invalid_payload),
                lambda: images.find_image(b"\xff\xd8missing-end"),
                lambda: images.find_image(PNG_BYTES, threshold=True),
                lambda: images.find_image(PNG_BYTES, threshold=-1),
                lambda: images.find_image(
                    PNG_BYTES,
                    threshold=images.MAX_COLOR_THRESHOLD + 1,
                ),
                lambda: images.find_image(PNG_BYTES, region=(0, 0, 0, 1)),
                lambda: images.find_image(PNG_BYTES, region=(0, 0, 1)),
            )
            for invalid in invalid_calls:
                with self.subTest(invalid=invalid), self.assertRaises((TypeError, ValueError)):
                    invalid()
            self.assertEqual(bytearray(b"not-an-image"), invalid_payload)
            self.assertEqual([], broker.calls)
        finally:
            _reset_execution_broker(token)

    def test_images_find_image_maps_host_failures_and_preserves_primary_error(self) -> None:
        for capability, code, error_type in (
            ("images.find_image", "ACCESSIBILITY_UNAVAILABLE", CapabilityUnavailableError),
            ("images.find_image", "SCREEN_CAPTURE_UNAVAILABLE", CapabilityUnavailableError),
            ("images.find_image", "SCREEN_CAPTURE_FAILED", HostCapabilityError),
            ("images.find_image", "RESULT_LIMIT_EXCEEDED", HostCapabilityError),
            ("images.find_image", "STALE_TEMPLATE", HostCapabilityError),
            ("images.write_template_chunk", "INVALID_IMAGE_TEMPLATE", HostCapabilityError),
        ):
            broker = RecordingBroker()
            broker.capability_failures[capability] = (code, "template search failure")
            token = _install_execution_broker(broker, EXECUTION_ID)
            try:
                with self.subTest(code=code), self.assertRaises(error_type) as captured:
                    images.find_image(JPEG_BYTES)
                if isinstance(captured.exception, HostCapabilityError):
                    self.assertEqual(code, captured.exception.code)
            finally:
                _reset_execution_broker(token)
            self.assertEqual("images.release_template", broker.calls[-1][0])

        primary = RecordingBroker()
        primary.capability_failures["images.find_image"] = (
            "SCREEN_CAPTURE_FAILED",
            "capture failed",
        )
        primary.capability_failures["images.release_template"] = (
            "HOST_FAILURE",
            "release also failed",
        )
        token = _install_execution_broker(primary, EXECUTION_ID)
        try:
            with self.assertRaises(HostCapabilityError) as captured:
                images.find_image(JPEG_BYTES)
            self.assertEqual("SCREEN_CAPTURE_FAILED", captured.exception.code)
        finally:
            _reset_execution_broker(token)
        self.assertEqual("images.release_template", primary.calls[-1][0])

        release_failed = RecordingBroker()
        release_failed.capability_failures["images.release_template"] = (
            "HOST_FAILURE",
            "release failed",
        )
        token = _install_execution_broker(release_failed, EXECUTION_ID)
        try:
            with self.assertRaises(HostCapabilityError) as captured:
                images.find_image(JPEG_BYTES)
            self.assertEqual("HOST_FAILURE", captured.exception.code)
        finally:
            _reset_execution_broker(token)

    def test_images_find_image_rejects_malformed_template_protocol_results(self) -> None:
        def mutate_final_dimensions(response: dict[str, object]) -> None:
            value = response["value"]
            if isinstance(value, dict) and value.get("complete") is True:
                value["width"] = images.MAX_TEMPLATE_DIMENSION + 1

        mutations = (
            (
                "images.begin_template",
                lambda response: response["value"].__setitem__("schema", "wrong"),
            ),
            (
                "images.begin_template",
                lambda response: response["value"].__setitem__("byteLength", 1),
            ),
            (
                "images.write_template_chunk",
                lambda response: response["value"].__setitem__("offset", 1),
            ),
            (
                "images.write_template_chunk",
                lambda response: response["value"].__setitem__(
                    "complete", not response["value"]["complete"]
                ),
            ),
            ("images.write_template_chunk", mutate_final_dimensions),
            (
                "images.find_image",
                lambda response: response["value"].__setitem__("schema", "wrong"),
            ),
            (
                "images.find_image",
                lambda response: response["value"].update(
                    {"found": False, "x": 0, "y": 0}
                ),
            ),
            (
                "images.find_image",
                lambda response: response["value"].update(
                    {"found": True, "x": 109, "y": 20}
                ),
            ),
        )
        for capability, mutator in mutations:
            broker = RecordingBroker()
            broker.capability_mutators[capability] = mutator
            token = _install_execution_broker(broker, EXECUTION_ID)
            try:
                with self.subTest(capability=capability), self.assertRaises(
                    HostCapabilityError
                ) as captured:
                    images.find_image(PNG_BYTES, region=(10, 20, 100, 200))
                self.assertEqual("BROKER_PROTOCOL_ERROR", captured.exception.code)
            finally:
                _reset_execution_broker(token)
            self.assertEqual("images.release_template", broker.calls[-1][0])

    def test_ocr_recognize_uploads_bounded_image_and_always_releases(self) -> None:
        broker = RecordingBroker()
        token = _install_execution_broker(broker, EXECUTION_ID)
        try:
            self.assertEqual(("AutoJs6", "中文 OCR"), ocr.recognize(memoryview(PNG_BYTES)))
        finally:
            _reset_execution_broker(token)

        self.assertEqual(
            [
                "images.begin_template",
                "images.write_template_chunk",
                "images.write_template_chunk",
                "ocr.recognize",
                "images.release_template",
            ],
            [capability for capability, _ in broker.calls],
        )
        self.assertEqual(
            {"templateId": "template-1"},
            broker.calls[-2][1],
        )
        self.assertEqual([("template-1", PNG_BYTES, "png")], broker.uploaded_templates)
        self.assertEqual(["template-1"], broker.template_releases)
        self.assertIsNone(broker.retained_template)

    def test_ocr_recognize_rejects_invalid_images_before_dispatch(self) -> None:
        broker = RecordingBroker()
        token = _install_execution_broker(broker, EXECUTION_ID)
        try:
            for invalid in ("png", [], b"", b"not-an-image"):
                with self.subTest(invalid=invalid), self.assertRaises((TypeError, ValueError)):
                    ocr.recognize(invalid)
            self.assertEqual([], broker.calls)
        finally:
            _reset_execution_broker(token)

    def test_ocr_recognize_maps_stable_failures_and_preserves_primary_error(self) -> None:
        for code, error_type in (
            ("OCR_UNAVAILABLE", CapabilityUnavailableError),
            ("OCR_FAILED", HostCapabilityError),
            ("RESULT_LIMIT_EXCEEDED", HostCapabilityError),
            ("STALE_TEMPLATE", HostCapabilityError),
        ):
            broker = RecordingBroker()
            broker.capability_failures["ocr.recognize"] = (code, "OCR failure")
            token = _install_execution_broker(broker, EXECUTION_ID)
            try:
                with self.subTest(code=code), self.assertRaises(error_type) as captured:
                    ocr.recognize(JPEG_BYTES)
                if isinstance(captured.exception, HostCapabilityError):
                    self.assertEqual(code, captured.exception.code)
            finally:
                _reset_execution_broker(token)
            self.assertEqual("images.release_template", broker.calls[-1][0])

        primary = RecordingBroker()
        primary.capability_failures["ocr.recognize"] = ("OCR_FAILED", "recognition failed")
        primary.capability_failures["images.release_template"] = (
            "HOST_FAILURE",
            "release also failed",
        )
        token = _install_execution_broker(primary, EXECUTION_ID)
        try:
            with self.assertRaises(HostCapabilityError) as captured:
                ocr.recognize(JPEG_BYTES)
            self.assertEqual("OCR_FAILED", captured.exception.code)
        finally:
            _reset_execution_broker(token)

    def test_ocr_recognize_rejects_malformed_or_oversized_results(self) -> None:
        malformed_values = (
            "not-a-list",
            [1],
            ["x"] * (ocr.MAX_LINES + 1),
            ["x" * (ocr.MAX_LINE_BYTES + 1)],
            ["x" * ocr.MAX_LINE_BYTES]
            * (ocr.MAX_TOTAL_TEXT_BYTES // ocr.MAX_LINE_BYTES + 1),
            ["\ud800"],
        )
        for malformed in malformed_values:
            broker = RecordingBroker()
            broker.capability_mutators["ocr.recognize"] = (
                lambda response, value=malformed: response.__setitem__("value", value)
            )
            token = _install_execution_broker(broker, EXECUTION_ID)
            try:
                with self.subTest(malformed=type(malformed).__name__), self.assertRaises(
                    HostCapabilityError
                ) as captured:
                    ocr.recognize(PNG_BYTES)
                self.assertEqual("BROKER_PROTOCOL_ERROR", captured.exception.code)
            finally:
                _reset_execution_broker(token)
            self.assertEqual("images.release_template", broker.calls[-1][0])

    def test_images_map_capture_lifecycle_failures_and_preserve_primary_errors(self) -> None:
        for code, error_type in (
            ("SCREEN_CAPTURE_UNAVAILABLE", CapabilityUnavailableError),
            ("SCREEN_CAPTURE_FAILED", HostCapabilityError),
            ("RESULT_LIMIT_EXCEEDED", HostCapabilityError),
        ):
            broker = RecordingBroker()
            broker.failure = (code, "screen capture failure")
            token = _install_execution_broker(broker, EXECUTION_ID)
            try:
                with self.subTest(code=code), self.assertRaises(error_type) as captured:
                    images.capture_screen()
                if isinstance(captured.exception, HostCapabilityError):
                    self.assertEqual(code, captured.exception.code)
            finally:
                _reset_execution_broker(token)

        stale = RecordingBroker()
        stale.capability_failures["images.read_chunk"] = (
            "STALE_IMAGE",
            "image is stale",
        )
        stale.capability_failures["images.release"] = (
            "HOST_FAILURE",
            "release also failed",
        )
        token = _install_execution_broker(stale, EXECUTION_ID)
        try:
            with self.assertRaises(HostCapabilityError) as captured:
                images.capture_screen()
            self.assertEqual("STALE_IMAGE", captured.exception.code)
        finally:
            _reset_execution_broker(token)
        self.assertEqual(
            ["images.capture_screen", "images.read_chunk", "images.release"],
            [capability for capability, _ in stale.calls],
        )

        release_failed = RecordingBroker()
        release_failed.capability_failures["images.release"] = (
            "HOST_FAILURE",
            "release failed",
        )
        token = _install_execution_broker(release_failed, EXECUTION_ID)
        try:
            with self.assertRaises(HostCapabilityError) as captured:
                images.capture_screen(format="jpeg")
            self.assertEqual("HOST_FAILURE", captured.exception.code)
        finally:
            _reset_execution_broker(token)

    def test_images_reject_malformed_descriptors_chunks_and_signatures(self) -> None:
        mutations = (
            (
                "images.capture_screen",
                lambda response: response["value"].__setitem__("sha256", "0" * 64),
            ),
            (
                "images.read_chunk",
                lambda response: response["value"].__setitem__("offset", 1),
            ),
            (
                "images.read_chunk",
                lambda response: response["value"].__setitem__("data", "%%"),
            ),
            (
                "images.read_chunk",
                lambda response: response["value"].__setitem__("eof", True),
            ),
        )
        for capability, mutator in mutations:
            broker = RecordingBroker()
            broker.capability_mutators[capability] = mutator
            token = _install_execution_broker(broker, EXECUTION_ID)
            try:
                with self.subTest(capability=capability), self.assertRaises(
                    HostCapabilityError
                ) as captured:
                    images.capture_screen()
                self.assertEqual("BROKER_PROTOCOL_ERROR", captured.exception.code)
            finally:
                _reset_execution_broker(token)
            self.assertEqual("images.release", broker.calls[-1][0])

        invalid_signature = RecordingBroker()
        invalid_signature.image_bytes_override = b"not-a-png"
        token = _install_execution_broker(invalid_signature, EXECUTION_ID)
        try:
            with self.assertRaises(HostCapabilityError) as captured:
                images.capture_screen()
            self.assertEqual("BROKER_PROTOCOL_ERROR", captured.exception.code)
        finally:
            _reset_execution_broker(token)
        self.assertEqual("images.release", invalid_signature.calls[-1][0])

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
