from __future__ import annotations

import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_ROOT = ROOT / "app" / "src" / "main" / "python"
RESULT_API = PYTHON_ROOT / "autojs6" / "result.py"
ARTIFACT_API = PYTHON_ROOT / "autojs6" / "artifacts.py"
CONTEXT = PYTHON_ROOT / "autojs6" / "_context.py"
BOOTSTRAP = PYTHON_ROOT / "autojs6_runtime" / "bootstrap.py"
KOTLIN_ROOT = (
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
)
METADATA = KOTLIN_ROOT / "PythonRuntimeMetadata.kt"
SESSION = KOTLIN_ROOT / "service" / "PythonExecutionSession.kt"
ARTIFACT_WORKSPACE = KOTLIN_ROOT / "transport" / "OutputArtifactWorkspace.kt"
ROADMAP = ROOT / "docs" / "legacy" / "ROADMAP-u1-en.md"
CONTRACT = ROOT / "docs" / "python" / "U1_R2_STRUCTURED_RESULTS_PROTOCOL.md"
VERIFIER = ROOT / "tools" / "verify-u1-r2-structured-results.ps1"
GITIGNORE = ROOT / ".gitignore"


class U1R2StructuredResultsSourceTest(unittest.TestCase):
    def test_result_is_explicit_canonical_json_and_never_derived_from_stdout(self) -> None:
        result_api = RESULT_API.read_text(encoding="utf-8")
        context = CONTEXT.read_text(encoding="utf-8")
        bootstrap = BOOTSTRAP.read_text(encoding="utf-8")

        self.assertIn("def set(value: Any) -> None:", result_api)
        self.assertIn("_set_structured_result(value)", result_api)
        self.assertIn("allow_nan=False", context)
        self.assertIn("sort_keys=True", context)
        self.assertIn('separators=(",", ":")', context)
        self.assertIn("structured JSON result was already set", context)
        self.assertIn('"structured_json": structured_json', bootstrap)
        self.assertIn("structured_json, artifact_paths = _execution_result_snapshot()", bootstrap)
        self.assertNotRegex(
            bootstrap,
            r"structured_json\s*=\s*(?:stdout|records)|json\.loads\([^\n]*(?:stdout|records)",
        )

    def test_artifact_api_accepts_only_registered_normalized_relative_paths(self) -> None:
        artifact_api = ARTIFACT_API.read_text(encoding="utf-8")
        context = CONTEXT.read_text(encoding="utf-8")

        self.assertIn("def path(relative_path: str) -> str:", artifact_api)
        self.assertIn("_register_artifact_path(relative_path)", artifact_api)
        for token in (
            'unicodedata.normalize("NFC", value) != value',
            'or "\\\\" in value',
            'segment in (".", "..")',
            "state.max_artifacts",
            "state.max_artifact_path_bytes",
            "os.path.commonpath",
        ):
            self.assertIn(token, context)

    def test_plugin_snapshots_regular_files_with_no_follow_and_digest_limits(self) -> None:
        workspace = ARTIFACT_WORKSPACE.read_text(encoding="utf-8")
        session = SESSION.read_text(encoding="utf-8")

        for token in (
            "Os.lstat(current.path)",
            "OsConstants.S_ISREG",
            "OsConstants.O_NOFOLLOW",
            "opened.st_dev == before.st_dev",
            "opened.st_ino == before.st_ino",
            "total <= maximumBytes",
            "aggregateBytes <= policy.maxTotalArtifactBytes",
            'MessageDigest.getInstance("SHA-256")',
            "ParcelFileDescriptor.MODE_READ_ONLY",
            "output.fd.sync()",
            "deleteTree(snapshotRoot, parent)",
        ):
            self.assertIn(token, workspace)
        self.assertIn("OutputArtifactWorkspace.create(", session)
        self.assertIn("validateResultAgainstPolicy(", session)
        self.assertIn("executionCallback.onResult(encoded, prepared.descriptors)", session)
        self.assertIn("onUndelivered = prepared::close", session)
        self.assertNotRegex(workspace, r"MODE_READ_WRITE|MODE_WRITE_ONLY")

    def test_protocol_14_capabilities_and_limits_are_truthfully_advertised(self) -> None:
        metadata = METADATA.read_text(encoding="utf-8")
        for token in (
            "supportsStructuredJsonResult = true",
            "supportsOutputArtifacts = true",
            "maxStructuredJsonBytes = 64 * 1024",
            "maxOutputArtifacts = 16",
            "maxOutputArtifactPathBytes = 1024",
            "maxOutputArtifactBytes = 4L * 1024L * 1024L",
            "maxTotalOutputArtifactBytes = 8L * 1024L * 1024L",
        ):
            self.assertIn(token, metadata)

    def test_contract_roadmap_and_gate_preserve_the_evidence_boundary(self) -> None:
        roadmap = ROADMAP.read_text(encoding="utf-8")
        contract = CONTRACT.read_text(encoding="utf-8")
        verifier = VERIFIER.read_text(encoding="utf-8")
        ignore = GITIGNORE.read_text(encoding="utf-8").splitlines()

        self.assertRegex(
            roadmap,
            re.compile(r"- \[x\] Add bounded structured JSON results and optional output artifacts"),
        )
        self.assertIn("Protocol 1.4 extension", contract)
        self.assertIn("Never infer", contract)
        for token in (
            "build/reports/python/u1/r2-structured-results-contract.json",
            "CURRENT_TREE_R2_STRUCTURED_RESULTS_PARTIAL_FUNCTIONAL_GATE",
            "phaseStatus = 'PARTIAL'",
            "protocolMinor14 = $hostScopedEvidencePassed",
            "structuredJsonResult = $pluginFunctionalPassed -and $hostScopedEvidencePassed",
            "outputArtifacts = $pluginFunctionalPassed -and $hostScopedEvidencePassed",
            "exactLengthAndSha256HostReceive = $hostScopedEvidencePassed",
            "r2Complete = $false",
            "hostFullAppSuiteExecuted = $false",
        ):
            self.assertIn(token, verifier)
        for claim in (
            "binderExecuted",
            "deviceVerified",
            "productionEvidence",
            "published",
            "releaseAuthorized",
        ):
            self.assertRegex(verifier, rf"{claim}\s*=\s*\$false")
        self.assertIn("!/tools/verify-u1-r2-structured-results.ps1", ignore)

    def test_verifier_contains_no_device_publication_or_external_mutation_command(self) -> None:
        body = VERIFIER.read_text(encoding="utf-8").lower()
        self.assertNotRegex(
            body,
            r"\badb(?:\.exe)?\b|connected[a-z]*test|instrumentation|install(?:debug|release)",
        )
        self.assertNotRegex(
            body,
            r"\bgh\b|git\s+(?:commit|push|tag)|verify-r6|publish(?:plugin|release|bundle)",
        )


if __name__ == "__main__":
    unittest.main()
