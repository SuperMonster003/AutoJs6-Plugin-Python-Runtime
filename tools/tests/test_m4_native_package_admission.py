from __future__ import annotations

import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
ADR = ROOT / "docs" / "adr" / "0004-native-python-package-admission.md"
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
            raise AssertionError(f"{path}:{line_number}: duplicate key {key!r}")
        result[key] = value
    return result


class M4NativePackageAdmissionTest(unittest.TestCase):
    def test_each_candidate_has_an_explicit_disposition(self) -> None:
        adr = ADR.read_text(encoding="utf-8")
        for marker in (
            "Decision code: `NOT_ADMITTED`",
            "Pillow: `BUILDABLE_NOT_ADMITTED_16K`",
            "NumPy: `BUILDABLE_NOT_ADMITTED_16K_AND_SIZE`",
            "OpenCV: `NOT_BUILDABLE_NO_CP313_WHEEL`",
            "`pillow==11.0.0`",
            "`numpy==1.26.2`",
            "`4.5.1.48-2`",
            "No matching",
            "distribution found",
        ):
            self.assertIn(marker, adr)

    def test_evaluation_inputs_and_apk_deltas_are_exact(self) -> None:
        adr = ADR.read_text(encoding="utf-8")
        for marker in (
            "`2ca45ea58b015c5e5df447ff77c6bae37bca571e`",
            "`b87eb2b5d7a31220b56f3ab19b1817065af3dd57997aff752132bc13e7832915`",
            "`0d380685ae11d55ab6ac8152b1eb79999913c458f412fa50d7cc9157558bd174`",
            "`5b24863b756d2a0adc0405a7c1a74f9acfd7c3aa66b920c8760daafc12a26da7`",
            "23,748,044",
            "23,764,404",
            "34,660,395",
            "+2,054,483",
            "+21,931,164",
            "`:app:assembleDebug --offline`",
            "`--no-index --find-links`",
        ):
            self.assertIn(marker, adr)

    def test_full_native_closure_records_dual_abi_16k_failures(self) -> None:
        adr = ADR.read_text(encoding="utf-8")
        for marker in (
            "Android's official guidance",
            "https://developer.android.com/guide/practices/page-sizes",
            "chaquopy-freetype 2.9.1-2",
            "chaquopy-libjpeg 1.5.3-1",
            "chaquopy-openblas 0.2.20-5",
            "chaquopy-libgfortran 4.9-0",
            "chaquopy-libcxx 180000-0",
            "`.so` or `.so.*`",
            "`llvm-readelf -lW`",
            "`0x1000`",
            "`0x4000`",
            "**fail both ABIs**",
            "**fail x86_64**",
            "`zipalign -c -P 16 4`",
            "must be relinked",
        ):
            self.assertIn(marker, adr)

    def test_future_native_gate_is_reproducible_licensed_and_measured(self) -> None:
        adr = " ".join(ADR.read_text(encoding="utf-8").split())
        for marker in (
            "immutable dual-ABI wheels",
            "same-major/minor CPython build tool",
            "`--require-hashes`",
            "network access denied",
            "Every LOAD segment",
            "all required license",
            "universal release APKs",
            "accepted size budget",
            "16 KiB-page environment",
            "known security exposure",
        ):
            self.assertIn(marker, adr)

    def test_current_runtime_still_contains_no_native_candidate(self) -> None:
        expected = {
            "python.packages.policy": "stdlib-only",
            "python.packages.count": "0",
            "online.pip.allowed": "false",
        }
        lock = load_unique_properties(LOCK)
        self.assertEqual(expected, {key: lock[key] for key in expected})

        build_gradle = BUILD_GRADLE.read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"(?m)^\s*pip\s*(?:\{|\()", build_gradle))

        candidate_roots = {"pil", "numpy", "cv2"}
        candidate_payloads: list[pathlib.Path] = []
        candidate_wheels: list[pathlib.Path] = []
        for root in (PYTHON_SOURCE, MAIN_ASSETS):
            for path in root.rglob("*"):
                if not path.is_file():
                    continue
                if path.suffix.lower() == ".whl":
                    candidate_wheels.append(path.relative_to(ROOT))
                if any(part.lower() in candidate_roots for part in path.parts):
                    candidate_payloads.append(path.relative_to(ROOT))
        self.assertEqual([], candidate_wheels)
        self.assertEqual([], candidate_payloads)

        notices = NOTICES.read_text(encoding="utf-8")
        self.assertIn("Pillow / NumPy / OpenCV native candidates", notices)
        self.assertIn("were evaluated but are not distributed", notices)
        self.assertIn("or a packaged dependency inventory", notices)

    def test_contract_policy_and_roadmap_publish_one_native_decision(self) -> None:
        policy = " ".join(POLICY.read_text(encoding="utf-8").split())
        semantics = " ".join(SEMANTICS.read_text(encoding="utf-8").split())
        roadmap = " ".join(ROADMAP.read_text(encoding="utf-8").split())
        for source in (policy, semantics, roadmap):
            self.assertIn("ADR 0004", source)
            self.assertIn("stdlib-only", source)
        self.assertIn("[x] [P] **路径 C (native 包评估)**", roadmap)
        self.assertIn("路径 B/C 均已评估且不接纳", roadmap)
        self.assertIn("`NOT_ADMITTED`", roadmap)
        self.assertIn("No native package was admitted", policy)
        self.assertIn("complete dual-ABI 16 KiB alignment gate", semantics)


if __name__ == "__main__":
    unittest.main()
