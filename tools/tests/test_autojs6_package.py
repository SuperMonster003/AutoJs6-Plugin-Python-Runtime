from __future__ import annotations

import json
import pathlib
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = ROOT / "app" / "src" / "main" / "python"
sys.path.insert(0, str(PYTHON_SOURCE))

from autojs6 import app, device, execution, project  # noqa: E402
from autojs6._context import _install_execution_context, _reset_execution_context  # noqa: E402
from autojs6.errors import (  # noqa: E402
    CapabilityUnavailableError,
    ProjectPathError,
    ProjectReadLimitError,
)
from autojs6_runtime.bootstrap import run_project, run_source  # noqa: E402


EXECUTION_ID = "12345678-1234-4234-8234-1234567890ab"


def capability_snapshot(*, project_files: bool = True) -> bytes:
    grants = ["app.snapshot.read", "device.snapshot.read"]
    if project_files:
        grants.append("project.files.read")
    return json.dumps(
        {
            "schemaVersion": 1,
            "execution": {
                "id": EXECUTION_ID,
                "entryPoint": "main.py",
                "project": project_files,
            },
            "grants": grants,
            "app": {
                "packageName": "org.autojs.autojs6",
                "versionName": "preview",
                "versionCode": 1,
                "debuggable": True,
            },
            "device": {
                "sdkInt": 31,
                "release": "12",
                "manufacturer": "example",
                "brand": "example",
                "model": "device",
                "supportedAbis": ["arm64-v8a"],
            },
        },
        separators=(",", ":"),
    ).encode("utf-8")


class AutoJs6PackageTest(unittest.TestCase):
    def test_missing_snapshot_fails_with_stable_capability_error(self) -> None:
        token = _install_execution_context(b"", None)
        try:
            for action in (execution.snapshot, app.snapshot, device.snapshot):
                with self.assertRaises(CapabilityUnavailableError):
                    action()
            with self.assertRaises(CapabilityUnavailableError):
                project.exists("data.txt")
        finally:
            _reset_execution_context(token)

    def test_frozen_snapshots_are_detached_from_internal_state(self) -> None:
        token = _install_execution_context(capability_snapshot(project_files=False), None)
        try:
            first = app.snapshot()
            first["packageName"] = "mutated"
            self.assertEqual("org.autojs.autojs6", app.snapshot()["packageName"])
            self.assertEqual(EXECUTION_ID, execution.snapshot()["id"])
            self.assertEqual(31, device.snapshot()["sdkInt"])
            with self.assertRaises(CapabilityUnavailableError):
                project.read_text("data.txt")
        finally:
            _reset_execution_context(token)

    def test_project_read_only_api_is_bounded_and_path_scoped(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            (root / "data.txt").write_text("hello", encoding="utf-8")
            (root / "binary.bin").write_bytes(b"\x00\x01")
            (root / "large.bin").write_bytes(b"x" * (project.MAX_READ_BYTES + 1))
            token = _install_execution_context(capability_snapshot(), str(root))
            try:
                self.assertEqual("hello", project.read_text("data.txt"))
                self.assertEqual(b"\x00\x01", project.read_bytes("binary.bin"))
                self.assertTrue(project.exists("data.txt"))
                self.assertFalse(project.exists("missing.txt"))
                with self.assertRaises(ProjectReadLimitError):
                    project.read_bytes("large.bin")
                for unsafe in (
                    "",
                    "/absolute",
                    "C:/absolute",
                    "dir\\file",
                    "dir//file",
                    "./file",
                    "../file",
                    "dir/../file",
                ):
                    with self.subTest(unsafe=unsafe), self.assertRaises(ProjectPathError):
                        project.exists(unsafe)
            finally:
                _reset_execution_context(token)

    def test_bootstrap_installs_snapshot_for_project_then_clears_it(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            source = (
                b"from autojs6 import app, device, execution, project\n"
                b"print(app.snapshot()['packageName'])\n"
                b"print(device.snapshot()['sdkInt'])\n"
                b"print(execution.snapshot()['id'])\n"
                b"print(project.read_text('data.txt'))\n"
            )
            (root / "main.py").write_bytes(source)
            (root / "data.txt").write_text("project-data", encoding="utf-8")

            outcome = run_project(
                source,
                "main.py",
                str(root),
                [],
                4096,
                256,
                128,
                capability_snapshot(),
            )

        self.assertEqual("completed", outcome["status"])
        output = b"".join(chunk for _, chunk in outcome["output"]).decode("utf-8")
        self.assertEqual(
            f"org.autojs.autojs6\n31\n{EXECUTION_ID}\nproject-data\n",
            output,
        )
        with self.assertRaises(CapabilityUnavailableError):
            app.snapshot()

    def test_standalone_bootstrap_without_snapshot_reports_capability_unavailable(self) -> None:
        outcome = run_source(
            b"from autojs6 import app\napp.snapshot()\n",
            "main.py",
            [],
            4096,
            256,
            128,
        )
        self.assertEqual("failed", outcome["status"])
        self.assertEqual("CapabilityUnavailableError", outcome["exception_type"])

    def test_duplicate_snapshot_key_is_rejected_before_install(self) -> None:
        malformed = capability_snapshot().replace(
            b'"schemaVersion":1',
            b'"schemaVersion":1,"schemaVersion":1',
            1,
        )
        with self.assertRaises(ValueError):
            _install_execution_context(malformed, None)


if __name__ == "__main__":
    unittest.main()
