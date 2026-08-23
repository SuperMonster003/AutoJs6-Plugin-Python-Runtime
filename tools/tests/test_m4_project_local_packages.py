from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "python" / "m4_project_local_requests"
GUIDE = ROOT / "docs" / "python" / "PROJECT_LOCAL_PACKAGES.md"
SEMANTICS = ROOT / "docs" / "python" / "PYTHON_SEMANTICS_CONTRACT.md"
STATIC_VERIFIER = ROOT / "tools" / "verify-r2-static.ps1"
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


class M4ProjectLocalPackagesTest(unittest.TestCase):
    def test_provider_and_readme_publish_the_same_workspace_profile(self) -> None:
        metadata = METADATA.read_text(encoding="utf-8")
        for declaration in (
            "maxWorkspaceArchiveBytes = 64L * 1024L * 1024L",
            "maxWorkspaceEntries = 8_192",
            "maxWorkspaceUncompressedBytes = 128L * 1024L * 1024L",
        ):
            self.assertIn(declaration, metadata)

        common = json.loads((ROOT / ".readme" / "common.json").read_text(encoding="utf-8"))
        self.assertEqual("64 MiB", common["max_workspace_archive_bytes"])
        self.assertEqual("8192", common["max_workspace_entries"])
        self.assertEqual("128 MiB", common["max_workspace_uncompressed_bytes"])

        verifier = STATIC_VERIFIER.read_text(encoding="utf-8")
        for assertion in (
            r"maxWorkspaceArchiveBytes\s*=\s*64L\s*\*\s*1024L\s*\*\s*1024L",
            r"maxWorkspaceEntries\s*=\s*8_192",
            r"maxWorkspaceUncompressedBytes\s*=\s*128L\s*\*\s*1024L\s*\*\s*1024L",
        ):
            self.assertIn(assertion, verifier)

    def test_example_is_reproducible_source_without_checked_in_packages(self) -> None:
        self.assertEqual(
            {"README.md", "main.py", "project.json", "requirements.txt"},
            {path.name for path in EXAMPLE.iterdir()},
        )
        self.assertEqual(
            {
                "type": "python",
                "main": "main.py",
                "timeout": 120000,
            },
            json.loads((EXAMPLE / "project.json").read_text(encoding="utf-8")),
        )
        self.assertEqual(
            [
                "requests==2.34.2",
                "urllib3==2.7.0",
                "certifi==2026.7.22",
                "charset-normalizer==3.4.9",
                "idna==3.18",
            ],
            (EXAMPLE / "requirements.txt").read_text(encoding="utf-8").splitlines(),
        )

        main = (EXAMPLE / "main.py").read_text(encoding="utf-8")
        for marker in (
            "requests_source.is_relative_to(project_root)",
            'requests.get("https://example.com/", timeout=15)',
            '"charset-normalizer"',
            "result.set(summary)",
        ):
            self.assertIn(marker, main)

    def test_guide_and_contract_keep_installation_explicit_and_bounded(self) -> None:
        guide = GUIDE.read_text(encoding="utf-8")
        semantics = SEMANTICS.read_text(encoding="utf-8")
        normalized_guide = " ".join(guide.split())
        normalized_semantics = " ".join(semantics.split())
        for marker in (
            "--target .",
            "--only-binary=:all:",
            "--platform any",
            "--python-version 3.13",
            "64 MiB",
            "8192",
            "128 MiB",
            "PYTHON_RUNTIME_WORKSPACE_INVALID",
            "PYTHON_RUNTIME_PROVIDER_INCOMPATIBLE",
            "ModuleNotFoundError",
        ):
            self.assertIn(marker, guide)
        for marker in (
            "project-local pure-Python",
            "64 MiB",
            "8192",
            "128 MiB",
            "ModuleNotFoundError",
        ):
            self.assertIn(marker, normalized_semantics)
        self.assertIn("never resolves a missing import", normalized_guide)
        self.assertIn("does not make hostile Python a security sandbox", normalized_guide)


if __name__ == "__main__":
    unittest.main()
