from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
TOOL_PATH = ROOT / "tools" / "verify-m6-candidate.py"
PROCESS = ROOT / "docs" / "maintenance" / "M6_RELEASE_PROCESS.md"
ROADMAP = ROOT / "ROADMAP.md"

SPEC = importlib.util.spec_from_file_location("verify_m6_candidate", TOOL_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class M6CandidateGateTest(unittest.TestCase):
    def test_properties_and_semver_are_strict(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            valid = root / "valid.properties"
            valid.write_text("# comment\nA=1\nB = two\n", encoding="utf-8")
            self.assertEqual({"A": "1", "B": "two"}, MODULE.read_unique_properties(valid))

            duplicate = root / "duplicate.properties"
            duplicate.write_text("A=1\nA=2\n", encoding="utf-8")
            with self.assertRaisesRegex(MODULE.CandidateError, "duplicate property"):
                MODULE.read_unique_properties(duplicate)

            malformed = root / "malformed.properties"
            malformed.write_text("not-a-property\n", encoding="utf-8")
            with self.assertRaisesRegex(MODULE.CandidateError, "malformed property"):
                MODULE.read_unique_properties(malformed)

        for version in ("0.5.0-alpha.6", "0.5.0-beta.1", "0.5.0", "1.0.0-rc.1"):
            MODULE.validate_version_name(version)
        for version in ("v0.5.0", "0.5", "01.0.0", "0.5.0-", "0.5.0-alpha..1"):
            with self.subTest(version=version):
                with self.assertRaises(MODULE.CandidateError):
                    MODULE.validate_version_name(version)

    def test_current_locale_generation_and_aar_lock_are_consistent(self) -> None:
        version = MODULE.read_unique_properties(ROOT / "version.properties")["VERSION_NAME"]
        common = json.loads((ROOT / ".readme" / "common.json").read_text(encoding="utf-8"))
        self.assertEqual("0.5.2", version)
        self.assertEqual(version, common["release_target"])
        self.assertEqual(10, MODULE.validate_changelog_sources(ROOT, version))
        self.assertEqual(25, MODULE.validate_generated_documents(ROOT))
        aar_count, host_head = MODULE.validate_host_api_aars(ROOT)
        self.assertEqual(3, aar_count)
        self.assertEqual("afca7b14c4ba3971b60a9ce3587e2f10bfd0ab1e", host_head)

    def test_profiles_are_local_debug_checks_without_release_mutation(self) -> None:
        source = TOOL_PATH.read_text(encoding="utf-8")
        compile(source, str(TOOL_PATH), "exec")
        for marker in (
            "--source-only",
            "--full",
            "AUTOJS6_PYTHON313",
            "python3.13",
            "-3.13",
            "PORTABLE_TESTS",
            "R2_STATIC",
            "pwsh.exe",
            "OFFLINE_DEBUG_BUILD",
            "--offline",
            ":app:testDebugUnitTest",
            ":app:assembleDebug",
            "NETWORK=NOT_USED",
            "ADB=NOT_USED",
            "SIGNING=NOT_USED",
            "PUBLICATION=NOT_PERFORMED",
        ):
            self.assertIn(marker, source)
        for forbidden in (
            '"adb"',
            "assemblerelease",
            "appenddigesttoreleasedfiles",
            "sign.properties",
            "git push",
            "git tag",
        ):
            self.assertNotIn(forbidden, source.lower())
        self.assertLess(
            source.index('shutil.which("pwsh.exe")'),
            source.index('shutil.which("powershell.exe")'),
        )
        self.assertIn("!/tools/verify-m6-candidate.py", (ROOT / ".gitignore").read_text())

    def test_process_and_roadmap_define_one_train_and_ten_smokes(self) -> None:
        process = PROCESS.read_text(encoding="utf-8")
        roadmap = ROADMAP.read_text(encoding="utf-8")
        checklist = process.split("## Manual Android smoke checklist (10 items)", 1)[1]
        checklist = checklist.split("## Signed candidate and publication boundary", 1)[0]
        self.assertEqual(10, checklist.count("- [ ]"))
        for marker in (
            "One cumulative release train",
            "0.2.x`, `0.3.x`, and `0.4.x",
            "0.5.0-alpha.N",
            "0.5.0-beta.1",
            "Accepted beta-to-stable-source run",
            "80FA480ACAE1C66C07DC59C9B588603B7F787E21DE72BB5A5521A2732B0C695F",
            "explicit user instruction",
            "never implied by either local M6 gate profile",
        ):
            self.assertIn(marker, process)
        for marker in (
            "**单一 release train**",
            "**轻量本地候选门禁**",
            "**十项真机冒烟清单**",
            "**精确 Host provenance**",
            "afca7b14c",
            "0.5.0-beta.1",
            "**beta 验收**",
            "**稳定候选源码**",
            "docs/maintenance/M6_RELEASE_PROCESS.md",
            "docs/maintenance/M6_ANDROID_SMOKE_RESULTS.md",
        ):
            self.assertIn(marker, roadmap)
        for stale in ("[ ] 发布 0.3.0-alpha", "[ ] 发布 0.3.x alpha", "[ ] 发布 0.4.0"):
            self.assertNotIn(stale, roadmap)
        self.assertNotIn("通过即发布", roadmap)


if __name__ == "__main__":
    unittest.main()
