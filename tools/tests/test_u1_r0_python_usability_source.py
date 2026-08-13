from __future__ import annotations

import json
import pathlib
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = ROOT / "app" / "src" / "main" / "python"
FIXTURE = ROOT / "tools" / "tests" / "fixtures" / "u1-r0-python-semantics-cases.json"
ROADMAP = ROOT / "ROADMAP.md"
CONTRACT = ROOT / "docs" / "python" / "PYTHON_SEMANTICS_CONTRACT.md"
VERIFIER = ROOT / "tools" / "verify-u1-r0-python-usability.ps1"

sys.path.insert(0, str(PYTHON_SOURCE))

from autojs6_runtime.bootstrap import run_project, run_source  # noqa: E402


ALLOWED_CURRENT_CLAIMS = {
    "VERIFIED_PORTABLE",
    "IMPLEMENTED_NOT_GATED",
    "CONTRACT_GAP",
    "UNSUPPORTED",
}
ALLOWED_TARGET_PHASES = {"R1", "R2", "R3", "R4", "R5", "R6"}
EXECUTABLE_KINDS = {"SOURCE", "PROJECT"}


def load_fixture() -> dict[str, object]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


class U1R0PythonUsabilitySourceTest(unittest.TestCase):
    def test_fixture_schema_and_evidence_boundary_are_fail_closed(self) -> None:
        document = load_fixture()
        self.assertEqual(1, document["schema"])
        self.assertEqual("U1", document["track"])
        self.assertEqual("R0", document["phase"])
        self.assertEqual(
            {
                "level": "PORTABLE_CPYTHON_ONLY",
                "androidCompiled": False,
                "binderExecuted": False,
                "deviceVerified": False,
                "published": False,
            },
            document["evidenceBoundary"],
        )
        target = document["targetRuntime"]
        self.assertEqual("CPython", target["implementation"])
        self.assertEqual("3.13.9", target["pythonVersion"])
        self.assertEqual("STRICT_UTF8_OPTIONAL_BOM", target["sourceEncodingTarget"])

    def test_case_ids_claims_and_execution_shapes_are_bounded(self) -> None:
        cases = load_fixture()["cases"]
        self.assertGreaterEqual(len(cases), 10)
        identifiers = [case["id"] for case in cases]
        self.assertEqual(len(identifiers), len(set(identifiers)))
        self.assertTrue(all(identifier == identifier.strip() and identifier for identifier in identifiers))

        categories: set[str] = set()
        for case in cases:
            categories.add(case["category"])
            self.assertIn(case["currentClaim"], ALLOWED_CURRENT_CLAIMS)
            self.assertIn(case["targetPhase"], ALLOWED_TARGET_PHASES)
            self.assertTrue(case["rationale"].strip())
            kind = case["execution"]["kind"]
            if case["currentClaim"] == "VERIFIED_PORTABLE":
                self.assertIn(kind, EXECUTABLE_KINDS)
                self.assertIsInstance(case["expected"], dict)
            else:
                self.assertEqual("NONE", kind)
                self.assertIsNone(case["expected"])

        self.assertTrue(
            {"syntax", "import", "execution-state", "error", "admission", "stdin", "dependency"}
            <= categories
        )

    def test_required_capability_and_gap_cases_remain_explicit(self) -> None:
        cases = {case["id"]: case for case in load_fixture()["cases"]}
        expected = {
            "source.encoding.strict-utf8": ("VERIFIED_PORTABLE", "R1"),
            "stdin.snapshot.input": ("VERIFIED_PORTABLE", "R1"),
            "project.entry.module-relative-import": ("VERIFIED_PORTABLE", "R1"),
            "package.third-party.offline-pack": ("UNSUPPORTED", "R3"),
        }
        for identifier, claim in expected.items():
            with self.subTest(identifier=identifier):
                self.assertIn(identifier, cases)
                self.assertEqual(claim, (cases[identifier]["currentClaim"], cases[identifier]["targetPhase"]))

    def test_verified_portable_cases_have_exact_bootstrap_outcomes(self) -> None:
        executable = [
            case for case in load_fixture()["cases"] if case["currentClaim"] == "VERIFIED_PORTABLE"
        ]
        self.assertGreaterEqual(len(executable), 7)
        for case in executable:
            with self.subTest(case=case["id"]):
                execution = case["execution"]
                kind = execution["kind"]
                if kind == "SOURCE":
                    stdin = execution.get("stdin", "").encode("utf-8")
                    outcome = run_source(
                        execution["source"].encode("utf-8"),
                        execution["entryPoint"],
                        list(execution["arguments"]),
                        64 * 1024,
                        4096,
                        1024,
                        b"",
                        stdin,
                    )
                elif kind == "PROJECT":
                    with tempfile.TemporaryDirectory() as directory:
                        root = pathlib.Path(directory)
                        for relative, text in execution["files"].items():
                            destination = root.joinpath(*relative.split("/"))
                            destination.parent.mkdir(parents=True, exist_ok=True)
                            destination.write_text(text, encoding="utf-8")
                        entry = root.joinpath(*execution["entryPoint"].split("/"))
                        outcome = run_project(
                            entry.read_bytes(),
                            execution["entryPoint"],
                            str(root),
                            list(execution["arguments"]),
                            64 * 1024,
                            4096,
                            1024,
                            b"",
                            execution.get("stdin", "").encode("utf-8"),
                        )
                else:  # pragma: no cover - schema test rejects this first
                    self.fail(f"Unsupported executable fixture kind: {kind}")

                expected = case["expected"]
                stdout = b"".join(
                    chunk for stream, chunk in outcome["output"] if stream == "stdout"
                ).decode("utf-8")
                stderr = b"".join(
                    chunk for stream, chunk in outcome["output"] if stream == "stderr"
                ).decode("utf-8")
                self.assertEqual(expected["status"], outcome["status"])
                self.assertEqual(expected["exitCode"], outcome["exit_code"])
                self.assertEqual(expected["stdout"], stdout)
                self.assertEqual(expected["stderr"], stderr)
                if "exceptionType" in expected:
                    self.assertEqual(expected["exceptionType"], outcome["exception_type"])

    def test_roadmap_contract_and_verifier_cross_reference_the_same_gate(self) -> None:
        roadmap = ROADMAP.read_text(encoding="utf-8")
        contract = CONTRACT.read_text(encoding="utf-8")
        verifier = VERIFIER.read_text(encoding="utf-8")
        report = "build/reports/python/u1/r0-python-usability-gate.json"
        fixture = "tools/tests/fixtures/u1-r0-python-semantics-cases.json"
        for body in (roadmap, contract, verifier):
            self.assertIn("U1", body)
            self.assertIn(report, body.replace("\\", "/"))
            self.assertIn(fixture, body.replace("\\", "/"))
        self.assertIn("Existing RC receipts are historical", roadmap)
        self.assertIn("production receipt", roadmap)
        self.assertNotRegex(verifier.lower(), r"\badb(?:\.exe)?\b|gradlew|connected[a-z]*test")


if __name__ == "__main__":
    unittest.main()
