from __future__ import annotations

import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
BOOTSTRAP = ROOT / "app" / "src" / "main" / "python" / "autojs6_runtime" / "bootstrap.py"
RUNTIME = ROOT / "app" / "src" / "main" / "java" / "io" / "github" / "supermonster003" / "autojs6" / "plugin" / "python" / "runtime" / "execution" / "ChaquopyRuntime.kt"
SINK = ROOT / "app" / "src" / "main" / "java" / "io" / "github" / "supermonster003" / "autojs6" / "plugin" / "python" / "runtime" / "execution" / "ChaquopyOutputSink.kt"
SESSION = ROOT / "app" / "src" / "main" / "java" / "io" / "github" / "supermonster003" / "autojs6" / "plugin" / "python" / "runtime" / "service" / "PythonExecutionSession.kt"
WORKSPACE = ROOT / "app" / "src" / "main" / "java" / "io" / "github" / "supermonster003" / "autojs6" / "plugin" / "python" / "runtime" / "transport" / "WorkspaceSnapshot.kt"
METADATA = ROOT / "app" / "src" / "main" / "java" / "io" / "github" / "supermonster003" / "autojs6" / "plugin" / "python" / "runtime" / "PythonRuntimeMetadata.kt"
HOST_AAR_LOCK = ROOT / "locks" / "host-api-aars.lock"
PROGUARD = ROOT / "app" / "proguard-rules.pro"
VERIFIER = ROOT / "tools" / "verify-u1-r2-module-io.ps1"
ROADMAP = ROOT / "docs" / "legacy" / "ROADMAP-u1-en.md"
GITIGNORE = ROOT / ".gitignore"


class U1R2ModuleAndOutputSourceTest(unittest.TestCase):
    def test_bootstrap_emits_through_execution_sink_and_keeps_portable_fallback(self) -> None:
        body = BOOTSTRAP.read_text(encoding="utf-8")
        self.assertIn("class _CollectingOutputSink", body)
        self.assertIn("if not self._output_sink.emit(self._stream, chunk):", body)
        self.assertIn("raise _OutputStopped()", body)
        self.assertRegex(body, r'except _OutputStopped:\s+return \{\s+"status": "stopped"')
        self.assertIn("output_sink_input: Any | None = None", body)

    def test_plugin_streams_before_outcome_and_retains_terminal_ordering_guards(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")
        session = SESSION.read_text(encoding="utf-8")
        sink = SINK.read_text(encoding="utf-8")
        self.assertIn("val outputSink = ChaquopyOutputSink(onOutput)", runtime)
        self.assertIn("outputSink.rethrowFailure()", runtime)
        self.assertIn("onOutput = ::emitOutput", session)
        self.assertNotIn("outcome.output.forEach(::emitOutput)", session)
        self.assertIn("while (state.get() == State.STARTED && outstandingCredits == 0)", session)
        self.assertIn("if (state.get() != State.STARTED) throw InterruptedException", session)
        self.assertIn("totalBytes > request.maxOutputBytes - record.bytes.size.toLong()", session)
        self.assertIn("throw PythonOutputLimitExceededException()", session)
        self.assertIn("synchronized(callbackOrder)", session)
        self.assertIn('@Synchronized\n    fun emit', sink)
        self.assertIn("User globals never receive this object", sink)
        self.assertNotRegex(sink, r"android\.content\.Context|android\.os\.IBinder|IPythonExecutionCallback")

    def test_module_entry_uses_runpy_and_file_mode_keeps_its_existing_branch(self) -> None:
        bootstrap = BOOTSTRAP.read_text(encoding="utf-8")
        runtime = RUNTIME.read_text(encoding="utf-8")
        workspace = WORKSPACE.read_text(encoding="utf-8")
        metadata = METADATA.read_text(encoding="utf-8")
        lock = HOST_AAR_LOCK.read_text(encoding="utf-8")

        self.assertIn('entry_mode not in ("file", "module")', bootstrap)
        self.assertIn("runpy.run_module(", bootstrap)
        self.assertIn('run_name="__main__"', bootstrap)
        self.assertIn("alter_sys=True", bootstrap)
        self.assertIn('"__spec__": None', bootstrap)
        self.assertIn("project_paths = [workspace_root]", bootstrap)
        self.assertIn("Python module source does not match its staged entry file", bootstrap)
        self.assertIn("_prepare_module_entry(logical_entry, entry_file)", bootstrap)
        self.assertIn("_find_module_spec(logical_entry)", bootstrap)
        self.assertIn("Python module entry does not resolve to its staged source file", bootstrap)
        self.assertIn("request.entryMode.bootstrapName()", runtime)
        self.assertIn("PythonRuntimeValidation.fileEntryPointForModuleName(entryPoint)", workspace)
        self.assertIn("supportsModuleEntry = true", metadata)
        self.assertRegex(lock, r"python-runtime-api\.sha256=[0-9a-f]{64}")
        self.assertNotIn("python-runtime-api.sha256=" + "0" * 64, lock)

    def test_reflective_sink_method_is_kept_for_minified_builds(self) -> None:
        rules = PROGUARD.read_text(encoding="utf-8")
        self.assertIn("runtime.execution.ChaquopyOutputSink", rules)
        self.assertIn("public boolean emit(java.lang.String, byte[]);", rules)

    def test_partial_gate_records_evidence_and_explicit_non_claims(self) -> None:
        body = VERIFIER.read_text(encoding="utf-8")
        for token in (
            "tools/tests",
            "test_*.py",
            ":app:testDebugUnitTest",
            ":app:assembleDebug",
            "build/reports/python/u1/r2-module-io-contract.json",
            "CURRENT_TREE_R2_MODULE_AND_OUTPUT_PARTIAL_FUNCTIONAL_GATE",
            "PORTABLE_CPYTHON_ONLY",
            "ANDROID_BUILD_ONLY",
            "r2Complete = $false",
            "explicitEntryMode = $pluginFunctionalPassed",
            "moduleRunpySemantics = $pluginFunctionalPassed",
            "protocolMinor12 = $hostScopedEvidencePassed",
            "hostApiChanged = $true",
            "structuredJsonResult = $false",
        ):
            self.assertIn(token, body)
        for token in (
            "hostPythonApiAndTargetedAppTests",
            "*PythonExecutionInputPolicyTest",
            "*PythonRuntimeProviderSelectionPolicyTest",
            "*PythonRuntimeHostPlanningTest",
            "*PythonHostCapabilitySnapshotTest",
            "HOST_PYTHON_JVM_TARGETED_ONLY",
            "hostFullAppSuiteExecuted = $false",
        ):
            self.assertIn(token, body)
        for claim in (
            "binderExecuted",
            "deviceVerified",
            "productionEvidence",
            "published",
            "releaseAuthorized",
        ):
            self.assertRegex(body, rf"{claim}\s*=\s*\$false")
        self.assertNotRegex(
            body.lower(),
            r"\badb(?:\.exe)?\b|connected[a-z]*test|instrumentation|install(?:debug|release)",
        )

    def test_roadmap_and_ignore_rules_expose_the_completed_module_and_output_subgates(self) -> None:
        roadmap = ROADMAP.read_text(encoding="utf-8")
        ignore = GITIGNORE.read_text(encoding="utf-8")
        self.assertRegex(
            roadmap,
            re.compile(
                r"- \[x\] Move stdout/stderr credit and backpressure into execution time,"
            ),
        )
        self.assertRegex(
            roadmap,
            re.compile(r"- \[x\] Add explicit `entryMode=file\|module`; module mode"),
        )
        self.assertIn("Current R2 status: module entry, execution-time output streaming", roadmap)
        self.assertIn("!/tools/verify-u1-r2-module-io.ps1", ignore.splitlines())

    def test_verifier_contains_no_external_mutation_or_publication_command(self) -> None:
        body = VERIFIER.read_text(encoding="utf-8").lower()
        self.assertNotRegex(
            body,
            r"\bgh\b|git\s+(?:commit|push|tag)|verify-r6|publish(?:plugin|release|bundle)",
        )


if __name__ == "__main__":
    unittest.main()
