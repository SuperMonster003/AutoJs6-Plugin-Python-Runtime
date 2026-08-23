from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HOST = ROOT.parent / "AutoJs6"
FIXTURE_PATH = ROOT / "tools" / "tests" / "fixtures" / "u1-r2-device-observation-contract.json"
RUNNER_WRAPPER_PATH = ROOT / "tools" / "device" / "run-u1-r2-binder-cpython-device.ps1"
RUNNER_CORE_PATH = ROOT / "tools" / "device" / "run-u1-r1-binder-cpython-device.ps1"
VERIFIER_WRAPPER_PATH = ROOT / "tools" / "verify-u1-r2-binder-cpython-device.ps1"
VERIFIER_CORE_PATH = ROOT / "tools" / "verify-u1-r1-binder-cpython-device.ps1"
FUNCTIONAL_GATE_PATH = ROOT / "tools" / "verify-u1-r2-e3-functional.ps1"
PUBLIC_TEST_PATH = (
    HOST
    / "app"
    / "src"
    / "androidTest"
    / "java"
    / "org"
    / "autojs"
    / "autojs"
    / "engine"
    / "PythonU1R2AcceptanceInstrumentationTest.kt"
)
BINDER_TEST_PATH = (
    HOST
    / "app"
    / "src"
    / "androidTest"
    / "java"
    / "org"
    / "autojs"
    / "autojs"
    / "core"
    / "plugin"
    / "python"
    / "PythonRuntimeU1R2BinderInstrumentationTest.kt"
)
CANCEL_TEST_PATH = BINDER_TEST_PATH.with_name("PythonRuntimeRealPluginCancelRebindDiagnosticTest.kt")
TIMEOUT_TEST_PATH = BINDER_TEST_PATH.with_name("PythonRuntimeRealPluginTimeoutRebindDiagnosticTest.kt")
R1_PUBLIC_TEST_PATH = PUBLIC_TEST_PATH.with_name("PythonU1R1AcceptanceInstrumentationTest.kt")
PROJECT_POLICY_PATH = (
    HOST
    / "app"
    / "src"
    / "main"
    / "java"
    / "org"
    / "autojs"
    / "autojs"
    / "script"
    / "PythonProjectLaunchPolicy.kt"
)
LAUNCH_FACTORY_PATH = PROJECT_POLICY_PATH.with_name("ScriptLaunchSourceFactory.kt")

FIXTURE = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
RUNNER_WRAPPER = RUNNER_WRAPPER_PATH.read_text(encoding="utf-8")
RUNNER_CORE = RUNNER_CORE_PATH.read_text(encoding="utf-8")
VERIFIER_WRAPPER = VERIFIER_WRAPPER_PATH.read_text(encoding="utf-8")
VERIFIER_CORE = VERIFIER_CORE_PATH.read_text(encoding="utf-8")
FUNCTIONAL_GATE = FUNCTIONAL_GATE_PATH.read_text(encoding="utf-8")
PUBLIC_TEST = PUBLIC_TEST_PATH.read_text(encoding="utf-8")
PROJECT_POLICY = PROJECT_POLICY_PATH.read_text(encoding="utf-8")
LAUNCH_FACTORY = LAUNCH_FACTORY_PATH.read_text(encoding="utf-8")
BINDER_TEST = BINDER_TEST_PATH.read_text(encoding="utf-8")
CANCEL_TEST = CANCEL_TEST_PATH.read_text(encoding="utf-8")
TIMEOUT_TEST = TIMEOUT_TEST_PATH.read_text(encoding="utf-8")


EXPECTED_SELECTORS = {
    "public-module-result-artifact": (
        "org.autojs.autojs.engine.PythonU1R2AcceptanceInstrumentationTest"
        "#publicModuleEngineReturnsExplicitJsonAndExactArtifactWithoutInferringStdout",
        {"autojs.python.u1r2.public.enabled": "true"},
        [
            "REAL_CPYTHON_3_13_9",
            "PUBLIC_ENGINE_MODULE_ENTRY",
            "MODULE_RUNPY_METADATA_AND_RELATIVE_IMPORT",
            "EXPLICIT_STRUCTURED_JSON_RESULT",
            "OUTPUT_ARTIFACT_EXACT_LENGTH_EOF_SHA256_BYTES",
            "HOST_OWNED_DEFENSIVE_ARTIFACT_BYTES",
            "STDOUT_RESULT_INFERENCE_FORBIDDEN",
            "ONE_STARTED_ONE_TERMINAL",
        ],
    ),
    "binder-interactive-stream": (
        "org.autojs.autojs.core.plugin.python.PythonRuntimeU1R2BinderInstrumentationTest"
        "#interactivePromptReplyStreamsBeforeTerminalAndKeepsStdoutOutOfResult",
        {"autojs.python.u1r2.binder.enabled": "true"},
        [
            "EXACT_COMPONENT_BIND",
            "PINNED_PROVIDER_CALLBACK_UID",
            "EXECUTION_TIME_ORDERED_STDOUT_BEFORE_PROMPT",
            "TYPED_PROMPT_ID_POLICY",
            "ONE_SHOT_BOUNDED_UTF8_REPLY",
            "STDOUT_RESULT_INFERENCE_FORBIDDEN",
            "ONE_STARTED_ONE_TERMINAL",
        ],
    ),
    "binder-artifact-limit-recovery": (
        "org.autojs.autojs.core.plugin.python.PythonRuntimeU1R2BinderInstrumentationTest"
        "#oversizedArtifactPublishesNoPartialResultThenNextExactBindSucceeds",
        {"autojs.python.u1r2.binder.enabled": "true"},
        [
            "RESULT_POLICY_PER_ARTIFACT_LIMIT",
            "OUTPUT_ARTIFACT_REJECTED_RESULT_PHASE",
            "NO_PARTIAL_RESULT_OR_DESCRIPTORS",
            "NEXT_EXACT_BIND_SUCCEEDS",
            "PINNED_PROVIDER_CALLBACK_UID",
            "ONE_STARTED_ONE_TERMINAL",
        ],
    ),
    "cancel-rebind": (
        "org.autojs.autojs.core.plugin.python.PythonRuntimeRealPluginCancelRebindDiagnosticTest"
        "#cancelAfterStartedKillsOldBinderThenExactRebindRunsFiniteRequestOnce",
        {"autojs.python.r2.cancelRebind.enabled": "true"},
        [
            "CANCEL_AFTER_STARTED",
            "TYPED_CANCELLATION",
            "OLD_PROVIDER_BINDER_DEATH",
            "NO_DISPATCH_REPLAY",
            "EXACT_REBIND_NEW_RUNTIME_GENERATION",
            "NEXT_FINITE_EXECUTION_SUCCEEDS",
            "PINNED_PROVIDER_CALLBACK_UID",
        ],
    ),
    "timeout-rebind": (
        "org.autojs.autojs.core.plugin.python.PythonRuntimeRealPluginTimeoutRebindDiagnosticTest"
        "#providerTimeoutFailsBeforeOldBinderDeathThenExactRebindRunsFiniteRequest",
        {"autojs.python.r2.timeoutRebind.enabled": "true"},
        [
            "PROVIDER_EXECUTION_TIMEOUT",
            "TYPED_TIMEOUT_BEFORE_BINDER_DEATH",
            "NO_HOST_CANCEL",
            "NO_DISPATCH_REPLAY",
            "EXACT_REBIND_NEW_RUNTIME_GENERATION",
            "NEXT_FINITE_EXECUTION_SUCCEEDS",
            "PINNED_PROVIDER_CALLBACK_UID",
        ],
    ),
}


class U1R2DeviceEvidenceSourceTest(unittest.TestCase):
    def test_fixture_freezes_five_independent_exact_selectors(self) -> None:
        self.assertEqual(FIXTURE["schemaVersion"], 1)
        self.assertEqual(FIXTURE["contract"], "AUTOJS6_PYTHON_RUNTIME_U1_R2_DEVICE_OBSERVATIONS")
        self.assertEqual(FIXTURE["track"], "U1")
        self.assertEqual(FIXTURE["phase"], "R2")
        self.assertEqual(
            FIXTURE["runnerComponent"],
            "org.autojs.autojs6.test/androidx.test.runner.AndroidJUnitRunner",
        )
        self.assertEqual(FIXTURE["instrumentationArguments"], {})
        self.assertEqual(len(FIXTURE["selectors"]), 5)
        selectors = {item["id"]: item for item in FIXTURE["selectors"]}
        self.assertEqual(set(selectors), set(EXPECTED_SELECTORS))
        for selector_id, (selector, arguments, covered) in EXPECTED_SELECTORS.items():
            self.assertEqual(selectors[selector_id]["selector"], selector)
            self.assertEqual(selectors[selector_id]["arguments"], arguments)
            self.assertEqual(selectors[selector_id]["covered"], covered)
            self.assertEqual(len(covered), len(set(covered)))

    def test_public_selector_uses_module_mode_and_host_owned_explicit_results(self) -> None:
        for marker in (
            'entryMode":"module","main":"$PACKAGE_NAME.main',
            "val launch = admittedProjectLaunch(projectRoot)",
            "val config = launch.createExecutionConfig()",
            "execution.config.getArgument(ENTRY_MODE_ARGUMENT)",
            "PythonRuntimeExecutionResult",
            "result.structuredJson",
            "result.outputArtifacts.single()",
            "PythonSha256.digest(ARTIFACT_BYTES)",
            "artifact.toByteArray()",
            "STDOUT_JSON_LOOKALIKE",
            "__spec__.name",
            "from .relative_value import VALUE",
            "artifacts.path",
            "result.set",
            "Host-owned artifact bytes must be defensive copies",
        ):
            self.assertIn(marker, PUBLIC_TEST)
        self.assertIn("stdout line was incorrectly inferred", PUBLIC_TEST)
        r1_source = R1_PUBLIC_TEST_PATH.read_text(encoding="utf-8")
        self.assertIn("as? PythonRuntimeExecutionResult", r1_source)
        self.assertIn("hostResult.terminal", r1_source)

    def test_public_project_stdin_path_is_explicit_bounded_and_device_exercised(self) -> None:
        for marker in (
            "projectManifestFileStdinFeedsSysStdinWithoutInteractivePrompt",
            r'\"stdin\":{\"file\":\"$STDIN_FILE_PATH\"}',
            "actual = sys.stdin.read()",
            'assert sys.stdin.read() == ""',
            "config.getArgument(STDIN_SNAPSHOT_ARGUMENT) as? ByteArray",
            "assertArrayEquals(expectedBytes, configuredStdin)",
            "assertPrivateTransportSnapshotsRemoved()",
        ):
            self.assertIn(marker, PUBLIC_TEST)
        for marker in (
            "PythonProjectStdinSource.InlineText",
            "PythonProjectStdinSource.ProjectFile",
            "stdinObject.size() != 1",
            "MAX_STDIN_SNAPSHOT_BYTES = 1L * 1024L * 1024L",
            "candidate.absoluteFile.path != normalizedFile.path",
            "PythonProjectLaunchError.STDIN_ESCAPES_ROOT",
        ):
            self.assertIn(marker, PROJECT_POLICY)
        self.assertIn("PythonProjectLaunchPolicy.snapshotStdin", LAUNCH_FACTORY)
        self.assertIn("PythonExecutionInputPolicy.STDIN_SNAPSHOT_ARGUMENT", LAUNCH_FACTORY)

    def test_binder_selectors_validate_prompt_order_result_independence_and_limit_recovery(self) -> None:
        for marker in (
            "PythonRuntimeCodec.decodeInputPrompt",
            "policy.onInputPrompt(prompt)",
            "policy.replyInput(reply)",
            ".replyInput(PythonRuntimeCodec.encodeInputReply(reply))",
            "observation.stdoutOrder < observation.promptOrder",
            "observation.replyOrder < observation.terminalOrder",
            "PythonInputEcho.VISIBLE",
            "PythonErrorCode.OUTPUT_ARTIFACT_REJECTED",
            "PythonFailurePhase.RESULT",
            "Rejected artifact session published a partial result",
            "Real Python Runtime identity changed after result rejection",
            "PythonProtocolVersion(1, 4)",
            "callback UID",
            "bound.binding.close()",
        ):
            self.assertIn(marker, BINDER_TEST)
        self.assertNotIn("Thread.sleep", BINDER_TEST)
        self.assertNotIn("SystemClock.sleep", BINDER_TEST)

    def test_reused_lifecycle_selectors_still_pin_opt_in_and_rebind_generation(self) -> None:
        self.assertIn("autojs.python.r2.cancelRebind.enabled", CANCEL_TEST)
        self.assertIn("cancelAfterStartedKillsOldBinderThenExactRebindRunsFiniteRequestOnce", CANCEL_TEST)
        self.assertIn("cancelled.runtimeGeneration", CANCEL_TEST)
        self.assertIn("completed.runtimeGeneration", CANCEL_TEST)
        self.assertIn("autojs.python.r2.timeoutRebind.enabled", TIMEOUT_TEST)
        self.assertIn("providerTimeoutFailsBeforeOldBinderDeathThenExactRebindRunsFiniteRequest", TIMEOUT_TEST)
        self.assertIn("typedTimeoutTerminalOrder", TIMEOUT_TEST)
        self.assertIn("binderDeathEventOrder", TIMEOUT_TEST)

    def test_shared_core_freezes_r2_fixture_content_without_weakening_r1(self) -> None:
        for source in (RUNNER_CORE, VERIFIER_CORE):
            self.assertIn("[ValidateSet('U1-R1', 'U1-R2')]", source)
            self.assertIn("AUTOJS6_PYTHON_RUNTIME_U1_R1_DEVICE_OBSERVATIONS", source)
            self.assertIn("AUTOJS6_PYTHON_RUNTIME_U1_R2_DEVICE_OBSERVATIONS", source)
            self.assertIn("u1-r1-device-observation-contract.json", source)
            self.assertIn("u1-r2-device-observation-contract.json", source)
            self.assertIn("$selectors.Count -eq $expectedObservationDefinitions.Count", source)
            self.assertIn("Observation fixture must be the canonical tracked U1-R1 contract", source)
            self.assertIn("Observation fixture must be the canonical tracked U1-R2 contract", source)
            for item in FIXTURE["selectors"]:
                self.assertIn(item["id"], source)
                self.assertIn(item["selector"], source)
                for key, value in item["arguments"].items():
                    self.assertIn(key, source)
                    self.assertIn(value, source)
                for covered in item["covered"]:
                    self.assertIn(covered, source)

    def test_r2_wrappers_require_exact_authority_and_force_r2_profile(self) -> None:
        runner_parameters = (
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
        for name in runner_parameters:
            self.assertRegex(
                RUNNER_WRAPPER,
                rf"\[Parameter\(Mandatory\s*=\s*\$true\)\][\s\S]{{0,180}}?\${name}(?:,|\s*\n)",
                name,
            )
        verifier_parameters = (
            "RawReport",
            "RawReportSha256",
            "ExpectedSerial",
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
        )
        for name in verifier_parameters:
            self.assertIn(f"{name} = ${name}", VERIFIER_WRAPPER)
        self.assertIn("EvidenceProfile = 'U1-R2'", RUNNER_WRAPPER)
        self.assertIn("EvidenceProfile = 'U1-R2'", VERIFIER_WRAPPER)
        self.assertIn("run-u1-r1-binder-cpython-device.ps1", RUNNER_WRAPPER)
        self.assertIn("verify-u1-r1-binder-cpython-device.ps1", VERIFIER_WRAPPER)

    def test_runner_remains_fail_closed_and_each_adb_call_is_serial_scoped(self) -> None:
        for marker in (
            "Pass -ConfirmNoActiveSoak explicitly",
            "Pass -ConfirmDeviceMutation explicitly",
            "ANDROID_SERIAL differs from -Serial",
            "Global\\AutoJs6-Codex-Device-",
            "A non-server adb.exe client prevents",
            "Assert-FullyAbsentPackageState",
            "Install-Artifact",
            "Assert-ArtifactEquivalent",
            "foreach ($definition in @($fixture.selectors))",
            "OK \\(1 test\\)",
            "AssumptionViolatedException",
            "for ($index = $contexts.Count - 1; $index -ge 0; $index--)",
            "FAILED_RESTORATION",
            "Raw output already exists and will not be overwritten",
            "r2-binder-cpython-device-run-",
        ):
            self.assertIn(marker, RUNNER_CORE)
        self.assertIn("@('-s', $Serial) + $Arguments", RUNNER_CORE)
        self.assertNotRegex(RUNNER_CORE.lower(), r"connected(?:android)?test|gradlew|gradle\.bat")
        self.assertNotIn("install', '-r'", RUNNER_CORE)

    def test_offline_verifier_recomputes_evidence_and_never_mutates_device(self) -> None:
        for marker in (
            "Raw report SHA-256 mismatch",
            "Split-InstrumentationSelector",
            "observed class does not prove the fixture class",
            "Record.startStatusCount -eq 1",
            "Record.successCodeCount -eq 1",
            "canonical output ignore-policy inspection",
            "r2-binder-cpython-device.json",
            "Canonical U1-R2 device evidence already exists and will not be overwritten",
        ):
            self.assertIn(marker, VERIFIER_CORE)
        self.assertNotRegex(VERIFIER_CORE, r"Invoke-NativeCapture\s+\$resolvedAdb")
        self.assertNotRegex(VERIFIER_CORE, r"Invoke-NativeCapture[^\n]+@\([^\)]*shell")
        for mutation in (" install ", " uninstall ", " pm clear ", " push ", " pull "):
            self.assertNotIn(mutation, VERIFIER_WRAPPER.lower())

    def test_r2_claims_are_device_partial_and_release_downgraded(self) -> None:
        for source in (RUNNER_CORE, VERIFIER_CORE):
            for marker in (
                "moduleEntryVerified",
                "executionTimeStreamingVerified",
                "interactiveInputVerified",
                "structuredJsonVerified",
                "outputArtifactsVerified",
                "resultLimitRecoveryVerified",
                "cancellationRecoveryVerified",
                "timeoutRecoveryVerified",
                "deviceMatrixVerified = $false",
                "productionEvidence = $false",
                "published = $false",
                "releaseAuthorized = $false",
                "NO_DEVICE_MATRIX",
                "NO_PUBLIC_RELEASE_VERIFICATION",
            ):
                self.assertIn(marker, source)
        self.assertIn("BINDER_CPYTHON_DEVICE_PARTIAL", RUNNER_CORE)
        self.assertIn("BINDER_CPYTHON_DEVICE_PARTIAL", VERIFIER_CORE)

    def test_functional_gate_binds_all_e2_contracts_and_packages_android_test_without_device_access(self) -> None:
        for marker in (
            "verify-u1-r2-module-io.ps1",
            "verify-u1-r2-interactive-input.ps1",
            "verify-u1-r2-structured-results.ps1",
            "CURRENT_TREE_R2_E3_FUNCTIONAL_GATE",
            "HOST_ANDROID_TEST_BUILD_ONLY",
            "hostPythonApiTests",
            "hostAndroidTestCompile",
            "hostAppPackage",
            "hostAndroidTestPackage",
            ":app:assembleAppDebug",
            ":app:compileAppDebugAndroidTestKotlin",
            ":app:assembleAppDebugAndroidTest",
            "phaseStatus -ceq 'PARTIAL'",
            "binderExecuted = $false",
            "deviceVerified = $false",
            "published = $false",
            "releaseAuthorized = $false",
        ):
            self.assertIn(marker, FUNCTIONAL_GATE)
        lowered = FUNCTIONAL_GATE.lower()
        self.assertNotIn(":app:testappdebugunittest", lowered)
        self.assertIn("hostfullappsuiteexecuted = $false", lowered)
        self.assertIn("python_api_and_frozen_r2_app_targets_only", lowered)
        self.assertNotRegex(lowered, r"\badb(?:\.exe)?\b")
        self.assertNotRegex(lowered, r"\b(?:install|uninstall|push|pull)\b")

    def test_tracking_files_expose_only_tools_not_generated_receipts(self) -> None:
        ignore = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn("!/tools/verify-u1-r2-binder-cpython-device.ps1", ignore)
        self.assertIn("!/tools/verify-u1-r2-e3-functional.ps1", ignore)
        self.assertIn("/build/", ignore)
        self.assertFalse((ROOT / "build" / "reports" / "python" / "u1" / "r2-binder-cpython-device.json").exists())

    def test_roadmap_and_operator_doc_keep_e3_open_until_offline_verified_device_evidence(self) -> None:
        roadmap = (ROOT / "docs" / "legacy" / "ROADMAP-u1-en.md").read_text(encoding="utf-8")
        operator = (ROOT / "docs" / "python" / "U1_R2_DEVICE_EVIDENCE.md").read_text(encoding="utf-8")
        normalized_operator = " ".join(operator.split())
        for marker in (
            "build/reports/python/u1/r2-e3-functional-gate.json",
            "build/reports/python/u1/r2-binder-cpython-device.json",
            "frozen five-selector observation fixture",
            "but no R2 device",
            "transaction or canonical R2 E3 report has been executed",
            "authorized explicit-serial run from clean commits",
            "5. [ ] Capture R2 exact-artifact Binder/CPython E3 evidence",
        ):
            self.assertIn(marker, roadmap)
        for marker in (
            "Status: tooling and instrumentation prepared; device transaction not executed.",
            "run-u1-r2-binder-cpython-device.ps1",
            "verify-u1-r2-binder-cpython-device.ps1",
            "U1_R2_BINDER_CPYTHON_EXACT_DEVICE_CELL",
            "The verifier performs no ADB operation.",
            "cannot be reused or renamed as R2 evidence",
            "Restoration failure is reported as `FAILED_RESTORATION`",
            "cannot substitute for it",
        ):
            self.assertIn(marker, normalized_operator, marker)


if __name__ == "__main__":
    unittest.main()
