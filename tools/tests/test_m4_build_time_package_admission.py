from __future__ import annotations

import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
ADR = ROOT / "docs" / "adr" / "0003-build-time-python-package-admission.md"
BUILD_GRADLE = ROOT / "app" / "build.gradle.kts"
LOCK = ROOT / "locks" / "python-runtime.lock"
POLICY = ROOT / "docs" / "maintenance" / "CPYTHON_RUNTIME_POLICY.md"
ROADMAP = ROOT / "ROADMAP.md"
SEMANTICS = ROOT / "docs" / "python" / "PYTHON_SEMANTICS_CONTRACT.md"
NOTICES = ROOT / "THIRD_PARTY_NOTICES.md"
PYTHON_SOURCE = ROOT / "app" / "src" / "main" / "python"
MAIN_ASSETS = ROOT / "app" / "src" / "main" / "assets"


def load_unique_properties(path: pathlib.Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line or line.startswith(("#", "!")):
            continue
        if "=" not in line:
            raise AssertionError(f"{path}:{line_number}: malformed property")
        key, value = (part.strip() for part in line.split("=", 1))
        if not key or key in result:
            raise AssertionError(f"{path}:{line_number}: empty or duplicate key {key!r}")
        result[key] = value
    return result


class M4BuildTimePackageAdmissionTest(unittest.TestCase):
    def test_embedded_runtime_stays_explicitly_stdlib_only(self) -> None:
        expected = {
            "python.packages.policy": "stdlib-only",
            "python.packages.count": "0",
            "online.pip.allowed": "false",
        }
        lock = load_unique_properties(LOCK)
        self.assertEqual(expected, {key: lock[key] for key in expected})

        build_gradle = BUILD_GRADLE.read_text(encoding="utf-8")
        for key, value in expected.items():
            self.assertIn(f'"{key}" to "{value}"', build_gradle)
        self.assertIsNone(
            re.search(r"(?m)^\s*pip\s*(?:\{|\()", build_gradle),
            "A Chaquopy pip block requires a new ADR 0003 admission decision",
        )

    def test_decision_records_reproducible_evidence_without_fake_delta(self) -> None:
        adr = ADR.read_text(encoding="utf-8")
        for marker in (
            "Decision code: `NOT_ADMITTED`",
            "`requests==2.34.2`",
            "`urllib3==2.7.0`",
            "`certifi==2026.7.22`",
            "`charset-normalizer==3.4.9`",
            "`idna==3.18`",
            "23,709,688",
            "23,726,048",
            "34,622,039",
            "880EBB02E4C264F9D8B82521C090F7592ABF0663E67BFC6DC4F224CB636F101B",
            "package delta is intentionally not reported",
            "chaquopy.pip_install",
            "Gradle's `--offline` state is not automatically passed",
        ):
            self.assertIn(marker, adr)

    def test_future_admission_gate_is_hermetic_licensed_and_measured(self) -> None:
        adr = ADR.read_text(encoding="utf-8")
        for marker in (
            "`--no-index`",
            "`--find-links`",
            "`--require-hashes`",
            "SHA-256",
            "license",
            "`py3-none-any`",
            "`.so`",
            "`.pyd`",
            "`.dll`",
            "`.dylib`",
            "`arm64-v8a`",
            "`x86_64`",
            "universal",
            "exact baseline and candidate byte delta",
            "`importlib.metadata`",
            "network access denied",
        ):
            self.assertIn(marker, adr)

    def test_no_candidate_payload_or_false_attribution_is_checked_in(self) -> None:
        blocked_package_roots = {
            "requests",
            "urllib3",
            "certifi",
            "charset_normalizer",
            "idna",
        }
        blocked_archives: list[pathlib.Path] = []
        blocked_sources: list[pathlib.Path] = []
        for root in (PYTHON_SOURCE, MAIN_ASSETS):
            for path in root.rglob("*"):
                if path.is_file() and (
                    path.name.lower().endswith(".whl")
                    or path.name.lower().endswith(".tar.gz")
                ):
                    blocked_archives.append(path.relative_to(ROOT))
                if any(part.lower() in blocked_package_roots for part in path.parts):
                    blocked_sources.append(path.relative_to(ROOT))
        self.assertEqual([], blocked_archives)
        self.assertEqual([], blocked_sources)
        self.assertFalse((ROOT / "third_party" / "python" / "wheelhouse").exists())

        notices = NOTICES.read_text(encoding="utf-8")
        self.assertIn("were evaluated but are not distributed", notices)
        self.assertIn("or a packaged dependency inventory", notices)

    def test_contract_policy_and_roadmap_publish_one_decision(self) -> None:
        policy = " ".join(POLICY.read_text(encoding="utf-8").split())
        semantics = " ".join(SEMANTICS.read_text(encoding="utf-8").split())
        roadmap = " ".join(ROADMAP.read_text(encoding="utf-8").split())
        for source in (policy, semantics, roadmap):
            self.assertIn("ADR 0003", source)
            self.assertIn("stdlib-only", source)
        self.assertIn("[x] [P] **路径 B (构建期精选包评估)**", roadmap)
        self.assertIn("`NOT_ADMITTED`", roadmap)
        self.assertIn("package count zero", semantics)
        self.assertIn("a bare `pip { install(...) }` is not sufficient", policy)


if __name__ == "__main__":
    unittest.main()
