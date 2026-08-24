from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "python" / "m5_long_running"
GUIDE = ROOT / "docs" / "python" / "LONG_RUNNING_EXECUTION.md"
SEMANTICS = ROOT / "docs" / "python" / "PYTHON_SEMANTICS_CONTRACT.md"
ROADMAP = ROOT / "ROADMAP.md"
METADATA = (
    ROOT
    / "app"
    / "src"
    / "main"
    / "java"
    / "io"
    / "github"
    / "supermonster003"
    / "autojs6"
    / "plugin"
    / "python"
    / "runtime"
    / "PythonRuntimeMetadata.kt"
)
SESSION = METADATA.parent / "service" / "PythonExecutionSession.kt"
HEARTBEAT_POLICY = METADATA.parent / "service" / "PythonHeartbeatPolicy.kt"


class M5LongRunningTest(unittest.TestCase):
    def test_provider_advertises_and_emits_protocol_heartbeat(self) -> None:
        metadata = METADATA.read_text(encoding="utf-8")
        session = SESSION.read_text(encoding="utf-8")
        policy = HEARTBEAT_POLICY.read_text(encoding="utf-8")

        self.assertIn("supportsLongRunningExecution = true", metadata)
        self.assertIn(
            "request.executionMode == PythonExecutionMode.BOUNDED", session
        )
        self.assertIn(
            "request.executionMode != PythonExecutionMode.LONG_RUNNING", session
        )
        self.assertIn(
            "PythonRuntimeContract.LONG_RUNNING_HEARTBEAT_INTERVAL_MILLIS", session
        )
        self.assertIn("executionCallback.onHeartbeat(encoded)", session)
        self.assertGreaterEqual(session.count("heartbeatFuture?.cancel(false)"), 3)
        self.assertIn("private var nextSequence = 1L", policy)
        self.assertIn("nowMillis - createdAtMillis", policy)
        self.assertIn("PythonRuntimeValidation::validateHeartbeat", policy)

    def test_example_is_explicit_unbounded_project_and_compiles(self) -> None:
        self.assertEqual(
            {"README.md", "main.py", "project.json"},
            {path.name for path in EXAMPLE.iterdir()},
        )
        self.assertEqual(
            {
                "type": "python",
                "main": "main.py",
                "executionMode": "long-running",
            },
            json.loads((EXAMPLE / "project.json").read_text(encoding="utf-8")),
        )
        source = (EXAMPLE / "main.py").read_text(encoding="utf-8")
        compile(source, str(EXAMPLE / "main.py"), "exec")
        self.assertIn("time.monotonic()", source)
        self.assertIn("flush=True", source)
        self.assertIn("time.sleep(5)", source)
        self.assertNotIn("import autojs6", source)

    def test_contract_documents_authorization_liveness_and_device_acceptance(self) -> None:
        guide = GUIDE.read_text(encoding="utf-8")
        semantics = SEMANTICS.read_text(encoding="utf-8")
        roadmap = ROADMAP.read_text(encoding="utf-8")
        normalized_guide = " ".join(guide.split())
        for marker in (
            '"executionMode": "long-running"',
            "mutually exclusive",
            "foreground user launch",
            "required-for-reader",
            "15 seconds",
            "45 seconds",
            "2 minutes",
            "Stop action",
            "process-restart cancellation",
            "QV710AF65F",
            "versionCode 5276",
            "versionCode 81",
            "tick=70",
            "roughly 350 seconds",
            "closes the focused M5 long-running Android smoke",
        ):
            self.assertIn(marker, normalized_guide)
        for marker in (
            "long-running",
            "protocol 1.6",
            "45-second",
            "foreground service",
        ):
            self.assertIn(marker, semantics)
        self.assertIn("长任务模式", roadmap)
        self.assertIn("**长任务 PASS**", roadmap)
        self.assertIn("Host versionCode 5276 / Plugin versionCode 81", roadmap)


if __name__ == "__main__":
    unittest.main()
