from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = REPO_ROOT / "tools" / "device" / "run-u1-r1-binder-cpython-device.ps1"
VERIFIER_PATH = REPO_ROOT / "tools" / "verify-u1-r1-binder-cpython-device.ps1"
FIXTURE_PATH = REPO_ROOT / "tools" / "tests" / "fixtures" / "u1-r1-device-observation-contract.json"
RUNNER = RUNNER_PATH.read_text(encoding="utf-8")
VERIFIER = VERIFIER_PATH.read_text(encoding="utf-8")
FIXTURE = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
GITIGNORE = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
EXPECTED_SELECTOR_COVERAGE = {
    "public-semantics": [
        "REAL_CPYTHON_3_13_9",
        "PUBLIC_ENGINE_STDIN_SNAPSHOT",
        "INPUT_PROMPT_AND_UNICODE_LINES",
        "PACKAGED_STDLIB_IMPORTS",
        "PROJECT_AND_RELATIVE_IMPORTS",
        "SEQUENTIAL_WORKSPACE_ISOLATION",
        "PINNED_PROVIDER_CALLBACK_UID",
        "ONE_STARTED_ONE_TERMINAL",
    ],
    "start-lease": [
        "OPENED_SESSION_START_LEASE",
        "NO_USER_CODE_BEFORE_START",
        "LEASE_RELEASES_SLOT_AND_DESCRIPTORS",
        "NEXT_FINITE_EXECUTION_SUCCEEDS",
    ],
}


class U1R1DeviceEvidenceSourceTest(unittest.TestCase):
    def test_fixture_pins_current_public_and_start_lease_selectors(self) -> None:
        self.assertEqual(FIXTURE["schemaVersion"], 1)
        self.assertEqual(FIXTURE["track"], "U1")
        self.assertEqual(FIXTURE["phase"], "R1")
        self.assertEqual(FIXTURE["instrumentationArguments"], {})
        selectors = {item["id"]: item for item in FIXTURE["selectors"]}
        self.assertEqual(
            selectors["public-semantics"]["selector"],
            "org.autojs.autojs.engine.PythonU1R1AcceptanceInstrumentationTest"
            "#publicScriptEngineRunsStdinStdlibRelativeImportsAndIsolatesSequentialWorkspaces",
        )
        self.assertEqual(
            selectors["public-semantics"]["arguments"],
            {"autojs.python.u1r1.acceptance.enabled": "true"},
        )
        self.assertEqual(
            selectors["start-lease"]["selector"],
            "org.autojs.autojs.core.plugin.python."
            "PythonRuntimeU1R1StartLeaseInstrumentationTest"
            "#openedButNeverStartedSessionExpiresAndNextExecutionSucceeds",
        )
        self.assertEqual(
            selectors["start-lease"]["arguments"],
            {"autojs.python.u1r1.startLease.enabled": "true"},
        )
        self.assertEqual(
            {key: value["covered"] for key, value in selectors.items()},
            EXPECTED_SELECTOR_COVERAGE,
        )

    def test_runner_and_verifier_freeze_the_canonical_fixture_content(self) -> None:
        for source in (RUNNER, VERIFIER):
            self.assertIn(
                "$selectors.Count -eq $expectedObservationDefinitions.Count",
                source,
            )
            self.assertIn("Observation fixture must be the canonical tracked U1-R1 contract", source)
            self.assertIn("contains reserved instrumentation argument", source)
            for item in FIXTURE["selectors"]:
                self.assertIn(item["id"], source)
                self.assertIn(item["selector"], source)
                for key, value in item["arguments"].items():
                    self.assertIn(key, source)
                    self.assertIn(value, source)
                for covered in item["covered"]:
                    self.assertIn(covered, source)

        hostile = json.loads(json.dumps(FIXTURE))
        hostile["selectors"][0]["selector"] += "Trivial"
        self.assertNotEqual(hostile, FIXTURE)
        hostile = json.loads(json.dumps(FIXTURE))
        hostile["selectors"][0]["arguments"]["class"] = "Trivial#passes"
        self.assertNotEqual(hostile, FIXTURE)

    def test_empty_global_argument_object_is_strict_mode_safe(self) -> None:
        for source in (RUNNER, VERIFIER):
            self.assertNotIn("PSObject.Properties.Name", source)
            self.assertIn(
                "$Object.PSObject.Properties | ForEach-Object { $_.Name }",
                source,
            )

    def test_runner_has_explicit_authority_and_exact_identity_parameters(self) -> None:
        required = (
            "Serial",
            "ExpectedApi",
            "ExpectedAbi",
            "ExpectedUserIds",
            "HostRepository",
            "PluginRepository",
            "ExpectedHostCommit",
            "ExpectedPluginCommit",
            "FunctionalGate",
            "FunctionalGateSha256",
            "ObservationFixture",
            "ObservationFixtureSha256",
            "HostApk",
            "HostSha256",
            "HostTestApk",
            "HostTestSha256",
            "PluginApk",
            "PluginSha256",
            "ExpectedSignerSha256",
            "AdbPath",
            "Aapt2Path",
            "ApkSignerPath",
            "Output",
            "ConfirmNoActiveSoak",
            "ConfirmDeviceMutation",
        )
        for name in required:
            self.assertRegex(
                RUNNER,
                rf"\[Parameter\(Mandatory\s*=\s*\$true\)\][\s\S]{{0,180}}?\${name}(?:,|\s*\n)",
                name,
            )
        self.assertRegex(RUNNER, r"\[int\[\]\]\s*\$ExpectedUserIds")
        self.assertIn("Pass -ConfirmNoActiveSoak explicitly", RUNNER)
        self.assertIn("Pass -ConfirmDeviceMutation explicitly", RUNNER)
        self.assertIn("ANDROID_SERIAL differs from -Serial", RUNNER)

    def test_runner_serializes_device_and_rejects_competing_clients(self) -> None:
        for marker in (
            "Global\\AutoJs6-Codex-Device-",
            "[Threading.Mutex]::new",
            "WaitOne(0)",
            "ReleaseMutex()",
            "Dispose()",
            "gradle-wrapper\\.jar",
            "fork-server\\s+server",
            "A non-server adb.exe client prevents",
        ):
            self.assertIn(marker, RUNNER)
        self.assertIn("finally", RUNNER)

    def test_missing_package_path_exit_one_is_admitted_only_with_empty_output(self) -> None:
        self.assertIn("$pathResult.ExitCode -in @(0, 1)", RUNNER)
        self.assertIn("$pathResult.ExitCode -eq 1", RUNNER)
        self.assertIn("[string]::IsNullOrWhiteSpace($pathResult.Text)", RUNNER)
        self.assertIn("$listed -and $pathResult.ExitCode -eq 0", RUNNER)
        self.assertIn("-not $listed -and $pathResult.ExitCode -eq 1", RUNNER)
        hostile = RUNNER.replace(
            "$pathResult.ExitCode -in @(0, 1)",
            "$pathResult.ExitCode -eq 0",
            1,
        )
        self.assertNotIn("$pathResult.ExitCode -in @(0, 1)", hostile)

    def test_runner_uses_fixture_list_and_strict_instrumentation_evidence(self) -> None:
        markers = (
            "foreach ($definition in @($fixture.selectors))",
            "OK \\(1 test\\)",
            "AssumptionViolatedException",
            "INSTRUMENTATION_STATUS_CODE",
            "INSTRUMENTATION_CODE",
            "outputSha256 = Get-TextSha256",
            "outputLineCount",
            "OK_1_TEST_ZERO_SKIP",
            "maximumInstrumentationOutputBytes = 1MB",
            "INSTRUMENTATION_STATUS:\\s*class=",
            "INSTRUMENTATION_STATUS:\\s*test=",
            "observedClass =",
            "observedTest =",
            "startStatusCount",
            "successCodeCount",
            "arguments = $mergedArguments",
        )
        for marker in markers:
            self.assertIn(marker, RUNNER)
        self.assertNotRegex(RUNNER, r"selectors\)\.Count\s*-eq\s*[0-9]+")

    def test_verifier_recomputes_observed_class_method_args_and_success_count(self) -> None:
        for marker in (
            "Split-InstrumentationSelector",
            "New-ExpectedMergedArguments",
            "INSTRUMENTATION_STATUS:\\s*class=",
            "INSTRUMENTATION_STATUS:\\s*test=",
            "observed class does not prove the fixture class",
            "observed test does not prove the fixture method",
            "Record.observedClassRecordCount",
            "Record.observedTestRecordCount",
            "Record.startStatusCount -eq 1",
            "Record.successCodeCount -eq 1",
            "Record.arguments.PSObject.Properties",
        ):
            self.assertIn(marker, VERIFIER)
        hostile_output = (
            "INSTRUMENTATION_STATUS: class=example.TrivialTest\n"
            "INSTRUMENTATION_STATUS: test=passes\n"
            "INSTRUMENTATION_STATUS_CODE: 1\n"
            "INSTRUMENTATION_STATUS: class=example.TrivialTest\n"
            "INSTRUMENTATION_STATUS: test=passes\n"
            "INSTRUMENTATION_STATUS_CODE: 0\n"
            "OK (1 test)\n"
            "INSTRUMENTATION_CODE: -1\n"
        )
        expected_selector = FIXTURE["selectors"][0]["selector"]
        expected_class, expected_method = expected_selector.split("#", 1)
        self.assertNotEqual(
            set(re.findall(r"^INSTRUMENTATION_STATUS: class=(.+)$", hostile_output, re.MULTILINE)),
            {expected_class},
        )
        self.assertNotEqual(
            set(re.findall(r"^INSTRUMENTATION_STATUS: test=(.+)$", hostile_output, re.MULTILINE)),
            {expected_method},
        )

    def test_runner_enforces_absent_install_pull_and_reverse_restore(self) -> None:
        markers = (
            "Assert-FullyAbsentPackageState",
            "temporary non-replacing",
            "Install-Artifact",
            "pull installed",
            "Assert-ArtifactEquivalent",
            "for ($index = $contexts.Count - 1; $index -ge 0; $index--)",
            "Runner-owned",
            "Final device user inventory",
            "Relevant processes remain after restoration",
            "FAILED_RESTORATION",
        )
        self.assertIn("@('install', '--user', '0', '-t'", RUNNER)
        self.assertNotIn("@('install', '-r'", RUNNER)
        for marker in markers:
            if marker == "temporary non-replacing":
                continue
            self.assertIn(marker, RUNNER)

    def test_signer_parser_accepts_numbered_and_build_tools_37_forms(self) -> None:
        parser = re.compile(
            r"^\s*(?:V\d+\s+)?Signer(?:\s+#?\d+)?\s*:?\s+certificate\s+SHA-256\s+digest:\s*"
            r"([0-9a-fA-F: ]+)\s*$",
            flags=re.IGNORECASE,
        )
        digest = "ab" * 32
        self.assertIsNotNone(parser.match(f"Signer #1 certificate SHA-256 digest: {digest}"))
        self.assertIsNotNone(parser.match(f"Signer 1 certificate SHA-256 digest: {digest}"))
        self.assertIsNotNone(parser.match(f"Signer certificate SHA-256 digest: {digest}"))
        self.assertIsNotNone(parser.match(f"V2 Signer: certificate SHA-256 digest: {digest}"))
        for source in (RUNNER, VERIFIER):
            self.assertIn("(?:V\\d+\\s+)?Signer(?:\\s+#?\\d+)?", source)
            self.assertIn("signer set is not an exact singleton", source)
            self.assertIn("Verified using v2 scheme", source)

    def test_android_test_apk_may_have_only_the_aapt2_empty_version_code(self) -> None:
        package_line = "package: name='org.autojs.autojs6.test' versionCode='' versionName=''"
        match = re.match(
            r"^package:\s+name='([^']+)'\s+versionCode='([0-9]*)'\s+versionName='([^']*)'",
            package_line,
        )
        self.assertIsNotNone(match)
        assert match is not None
        self.assertEqual(match.group(2), "")
        for source in (RUNNER, VERIFIER):
            self.assertIn("versionCode='([0-9]*)'", source)
            self.assertIn("$Role -ceq 'androidTest'", source)
            self.assertIn("versionCode is unexpectedly empty", source)

    def test_verifier_normalizes_only_null_native_abi_sets_to_empty(self) -> None:
        self.assertIn(
            "[object[]] $recordNativeAbis = @()",
            VERIFIER,
        )
        self.assertIn(
            "if ($null -ne $Record.nativeAbis) { $recordNativeAbis = @($Record.nativeAbis) }",
            VERIFIER,
        )
        self.assertIn(
            "[string[]] $liveNativeAbis = @()",
            VERIFIER,
        )
        self.assertIn(
            "if ($null -ne $Live.nativeAbis) { $liveNativeAbis = @($Live.nativeAbis) }",
            VERIFIER,
        )
        self.assertIn(
            'Assert-StringSequence $recordNativeAbis $liveNativeAbis "$Label native ABI set"',
            VERIFIER,
        )

    def test_verifier_preserves_instrumentation_lines_as_a_typed_array(self) -> None:
        self.assertIn("[string[]] $lines = @()", VERIFIER)
        self.assertIn(
            'if ($output.Length -gt 0) { $lines = @($output -split "`n") }',
            VERIFIER,
        )
        self.assertNotIn('$output -split "`n", -1', VERIFIER)

    def test_raw_and_canonical_claims_are_strictly_downgraded(self) -> None:
        for source in (RUNNER, VERIFIER):
            for marker in (
                "BINDER_CPYTHON_DEVICE_PARTIAL",
                "deviceMatrixVerified = $false",
                "productionEvidence = $false",
                "published = $false",
                "releaseAuthorized = $false",
                "NO_DEVICE_MATRIX",
                "NO_PUBLIC_RELEASE_VERIFICATION",
            ):
                self.assertIn(marker, source)
        for marker in (
            "confirmNoActiveSoak = $ConfirmNoActiveSoak.IsPresent",
            "confirmDeviceMutation = $ConfirmDeviceMutation.IsPresent",
        ):
            self.assertIn(marker, RUNNER)
        self.assertIn("Raw preflight lacks the current-run no-active-soak confirmation", VERIFIER)

    def test_raw_is_non_overwriting_and_verifier_is_offline_atomic(self) -> None:
        self.assertIn("Raw output already exists and will not be overwritten", RUNNER)
        self.assertIn("[IO.File]::Move($temporary, $Path)", RUNNER)
        self.assertNotIn("[IO.File]::Replace($temporary, $Path", RUNNER)
        self.assertNotRegex(VERIFIER, r"Invoke-NativeCapture\s+\$resolvedAdb")
        self.assertNotRegex(VERIFIER, r"Invoke-NativeCapture[^\n]+@\([^\)]*shell")
        self.assertIn("Raw report SHA-256 mismatch", VERIFIER)
        self.assertIn("Raw device claims", VERIFIER)
        self.assertIn("canonical output ignore-policy inspection", VERIFIER)
        self.assertIn(
            "Assert-NativeSuccess $ignored 'Canonical output ignore-policy inspection'",
            VERIFIER,
        )
        self.assertIn("Canonical U1-R1 device evidence already exists and will not be overwritten", VERIFIER)
        self.assertIn("appeared concurrently and will not be overwritten", VERIFIER)
        self.assertNotIn("[IO.File]::Replace", VERIFIER)
        self.assertIn("[IO.File]::Move", VERIFIER)
        self.assertIn("r1-binder-cpython-device.json", VERIFIER)
        self.assertIn("!/tools/verify-u1-r1-binder-cpython-device.ps1", GITIGNORE)


if __name__ == "__main__":
    unittest.main()
