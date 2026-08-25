from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "python" / "m6_manual_smoke"
RESULTS = ROOT / "docs" / "maintenance" / "M6_ANDROID_SMOKE_RESULTS.md"
PYTHON_SOURCE = ROOT / "app" / "src" / "main" / "python"
sys.path.insert(0, str(PYTHON_SOURCE))

from autojs6_runtime.bootstrap import run_project, run_source  # noqa: E402


def captured_output(outcome: dict[str, object]) -> str:
    return b"".join(chunk for _, chunk in outcome["output"]).decode("utf-8")


def structured_result(outcome: dict[str, object]) -> dict[str, object]:
    encoded = outcome["structured_json"]
    assert isinstance(encoded, str)
    value = json.loads(encoded)
    assert isinstance(value, dict)
    return value


class InputBridge:
    def __init__(self, *responses: str) -> None:
        self.responses = list(responses)
        self.calls: list[tuple[str, str]] = []

    def request(self, prompt: str, echo: str) -> str:
        self.calls.append((prompt, echo))
        if not self.responses:
            raise AssertionError("unexpected interactive prompt")
        return self.responses.pop(0)


class M6ManualSmokeTest(unittest.TestCase):
    def test_sources_manifests_and_operator_contract_are_well_formed(self) -> None:
        self.assertTrue(EXAMPLE.is_dir())
        for path in EXAMPLE.rglob("*.py"):
            compile(path.read_bytes(), str(path), "exec")
        manifests = list(EXAMPLE.rglob("project.json"))
        self.assertEqual(6, len(manifests))
        for path in manifests:
            self.assertEqual("python", json.loads(path.read_text(encoding="utf-8"))["type"])

        guide = (EXAMPLE / "README.md").read_text(encoding="utf-8")
        verifier = (EXAMPLE / "verify-m6-04-artifact.ps1").read_text(encoding="utf-8")
        results = RESULTS.read_text(encoding="utf-8")
        for marker in (
            "stateCounter=1",
            "AUTOJS6-VISIBLE",
            "M6-HIDDEN-7f3a",
            "M6-03-BACKGROUND-PASS",
            "M6-04-NO-RESULT-PASS",
            "verify-m6-04-artifact.ps1",
        ):
            self.assertIn(marker, guide)
        for marker in (
            "ValidatePattern",
            "adb -s $Serial pull",
            "$expectedBytes = 34L",
            "Get-FileHash",
            "M6-04-ARTIFACT-PASS",
            "Remove-Item -LiteralPath $temporaryFile",
        ):
            self.assertIn(marker, verifier)
        for marker in (
            "QV710AF65F exact SM003 alpha.6 candidate run",
            "QV710AF65F exact SM003 beta.1 candidate run",
            "every item PASS",
            "CA6252ACE475FFA554FE414DEB09386F0F5BED79F2CC135847FEF9A3424FD8ED",
            "80FA480ACAE1C66C07DC59C9B588603B7F787E21DE72BB5A5521A2732B0C695F",
            "alpha-to-beta",
            "beta-to-stable-source",
        ):
            self.assertIn(marker, results)

    def test_file_and_module_import_projects_pass_and_restore_modules(self) -> None:
        file_root = EXAMPLE / "m6_02_file_entry"
        file_outcome = run_project(
            (file_root / "src" / "main.py").read_bytes(),
            "src/main.py",
            str(file_root),
            [],
            65536,
            4096,
            256,
            max_structured_json_bytes=65536,
        )
        self.assertEqual("completed", file_outcome["status"])
        self.assertTrue(structured_result(file_outcome)["allChecks"])
        self.assertIn("M6-02-FILE-ENTRY-PASS", captured_output(file_outcome))

        module_root = EXAMPLE / "m6_02_imports"
        module_source = (module_root / "smoke_imports" / "main.py").read_bytes()
        for _ in range(2):
            outcome = run_project(
                module_source,
                "smoke_imports.main",
                str(module_root),
                [],
                65536,
                4096,
                256,
                entry_mode="module",
                max_structured_json_bytes=65536,
            )
            self.assertEqual("completed", outcome["status"])
            value = structured_result(outcome)
            self.assertTrue(value["allChecks"])
            self.assertEqual(1, value["stateCounter"])
            self.assertEqual("1.2.3", value["dependencyVersion"])
            self.assertIn("M6-02-IMPORTS-PASS", captured_output(outcome))

        for module_name in (
            "root_helper",
            "sibling_helper",
            "plain_module",
            "smoke_imports",
            "smoke_imports.main",
            "vendored_probe",
            "vendored_transport",
        ):
            self.assertNotIn(module_name, sys.modules)

    def test_snapshot_foreground_background_and_cancel_inputs(self) -> None:
        snapshot_root = EXAMPLE / "m6_03a_stdin_snapshot"
        snapshot = run_project(
            (snapshot_root / "main.py").read_bytes(),
            "main.py",
            str(snapshot_root),
            [],
            65536,
            4096,
            256,
            stdin_input=(snapshot_root / "fixtures" / "input.txt").read_bytes(),
            max_structured_json_bytes=65536,
        )
        self.assertEqual("completed", snapshot["status"])
        self.assertEqual(
            {
                "case": "M6-03A",
                "first": "快照值 αβ",
                "rest": "剩余行 Ω\n",
                "eof": True,
            },
            structured_result(snapshot),
        )

        bridge = InputBridge("\u0001AUTOJS6-VISIBLE", "\u0001M6-HIDDEN-7f3a")
        foreground = run_source(
            (EXAMPLE / "m6_03b_foreground_input.py").read_bytes(),
            "m6_03b_foreground_input.py",
            [],
            65536,
            4096,
            256,
            input_bridge_input=bridge,
            max_structured_json_bytes=65536,
        )
        self.assertEqual("completed", foreground["status"])
        self.assertEqual(["visible", "hidden"], [echo for _, echo in bridge.calls])
        self.assertNotIn("M6-HIDDEN-7f3a", captured_output(foreground))
        self.assertTrue(structured_result(foreground)["getpassMatched"])

        background_root = EXAMPLE / "m6_03c_background_input"
        background = run_project(
            (background_root / "main.py").read_bytes(),
            "main.py",
            str(background_root),
            [],
            65536,
            4096,
            256,
            max_structured_json_bytes=65536,
        )
        self.assertEqual("completed", background["status"])
        self.assertEqual("EOFError", structured_result(background)["error"])

        cancel_bridge = InputBridge("\u0003")
        cancelled = run_source(
            (EXAMPLE / "m6_03d_foreground_cancel.py").read_bytes(),
            "m6_03d_foreground_cancel.py",
            [],
            65536,
            4096,
            256,
            input_bridge_input=cancel_bridge,
            max_structured_json_bytes=65536,
        )
        self.assertEqual("completed", cancelled["status"])
        self.assertTrue(structured_result(cancelled)["cancelled"])

    def test_result_artifact_and_no_result_paths(self) -> None:
        artifact_root = EXAMPLE / "m6_04a_result_artifact"
        with tempfile.TemporaryDirectory() as output_root:
            artifact = run_project(
                (artifact_root / "main.py").read_bytes(),
                "main.py",
                str(artifact_root),
                [],
                65536,
                4096,
                256,
                output_artifact_root=output_root,
                max_structured_json_bytes=65536,
                max_output_artifacts=8,
                max_output_artifact_path_bytes=512,
            )
            payload = (Path(output_root) / "m6" / "expected.bin").read_bytes()
        self.assertEqual("completed", artifact["status"])
        self.assertEqual(34, len(payload))
        self.assertEqual(("m6/expected.bin",), artifact["artifact_paths"])
        self.assertEqual(
            "2B4A5E4BB7EB7C83D6241C5176D01EEDD31873FA63B28DE10F5553D8FBD25BD4",
            structured_result(artifact)["sha256"],
        )

        no_result_root = EXAMPLE / "m6_04b_no_explicit_result"
        no_result = run_project(
            (no_result_root / "main.py").read_bytes(),
            "main.py",
            str(no_result_root),
            [],
            65536,
            4096,
            256,
            max_structured_json_bytes=65536,
        )
        self.assertEqual("completed", no_result["status"])
        self.assertIsNone(no_result["structured_json"])
        self.assertEqual((), no_result["artifact_paths"])
        self.assertIn(
            '{"fabricated":true,"source":"stdout-only"}',
            captured_output(no_result),
        )


if __name__ == "__main__":
    unittest.main()
