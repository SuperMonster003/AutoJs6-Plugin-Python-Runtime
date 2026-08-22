from __future__ import annotations

import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
BOOTSTRAP = ROOT / "app" / "src" / "main" / "python" / "autojs6_runtime" / "bootstrap.py"
BRIDGE = ROOT / "app" / "src" / "main" / "java" / "io" / "github" / "supermonster003" / "autojs6" / "plugin" / "python" / "runtime" / "execution" / "ChaquopyInputBridge.kt"
RUNTIME = ROOT / "app" / "src" / "main" / "java" / "io" / "github" / "supermonster003" / "autojs6" / "plugin" / "python" / "runtime" / "execution" / "ChaquopyRuntime.kt"
SESSION = ROOT / "app" / "src" / "main" / "java" / "io" / "github" / "supermonster003" / "autojs6" / "plugin" / "python" / "runtime" / "service" / "PythonExecutionSession.kt"
METADATA = ROOT / "app" / "src" / "main" / "java" / "io" / "github" / "supermonster003" / "autojs6" / "plugin" / "python" / "runtime" / "PythonRuntimeMetadata.kt"
PROGUARD = ROOT / "app" / "proguard-rules.pro"
ROADMAP = ROOT / "docs" / "legacy" / "ROADMAP-u1-en.md"
CONTRACT = ROOT / "docs" / "python" / "U1_R2_INTERACTIVE_INPUT_PROTOCOL.md"
VERIFIER = ROOT / "tools" / "verify-u1-r2-interactive-input.ps1"
GITIGNORE = ROOT / ".gitignore"


class U1R2InteractiveInputSourceTest(unittest.TestCase):
    def test_bootstrap_patches_only_builtin_input_and_restores_it(self) -> None:
        body = BOOTSTRAP.read_text(encoding="utf-8")
        self.assertIn("def _interactive_input(prompt: Any, input_bridge: Any) -> str:", body)
        self.assertIn("line = sys.stdin.readline()", body)
        self.assertIn('input_bridge.request(prompt_text, "visible")', body)
        self.assertIn("raise EOFError", body)
        self.assertIn("raise KeyboardInterrupt", body)
        self.assertIn("previous_builtin_input = builtins.input", body)
        self.assertIn("builtins.input = previous_builtin_input", body)
        self.assertNotRegex(body, r"sys\.stdin\s*=\s*input_bridge")

    def test_private_bridge_is_narrow_and_never_carries_host_objects(self) -> None:
        bridge = BRIDGE.read_text(encoding="utf-8")
        runtime = RUNTIME.read_text(encoding="utf-8")
        rules = PROGUARD.read_text(encoding="utf-8")
        self.assertIn("class ChaquopyInputBridge", bridge)
        self.assertIn("fun request(prompt: String, echo: String): String", bridge)
        self.assertIn("inputBridge?.rethrowFailure()", runtime)
        self.assertIn("inputBridge", runtime)
        self.assertNotRegex(
            bridge,
            r"android\.content\.Context|android\.os\.IBinder|IPythonExecutionCallback|Bundle",
        )
        self.assertIn("runtime.execution.ChaquopyInputBridge", rules)
        self.assertIn(
            "public java.lang.String request(java.lang.String, java.lang.String);",
            rules,
        )

    def test_session_enforces_one_typed_reply_and_wakes_on_every_terminal_path(self) -> None:
        body = SESSION.read_text(encoding="utf-8")
        for token in (
            "override fun replyInput(reply: ByteArray?)",
            "decoded.requestId != request.requestId",
            "decoded.promptId != pending.prompt.promptId",
            "pending.reply != null",
            "PythonPromptId.fromLong(nextInputPromptId)",
            "inputPromptCount >= inputPolicy.maxPrompts",
            "while (state.get() == State.STARTED && pending.reply == null)",
            "throw PythonInputTimeoutException()",
            "workerFuture?.cancel(true)",
            "fun serviceDestroyed()",
            "private fun deadlineReached()",
            "private fun callbackDied()",
            "private fun hardRetire()",
            "retirement.retireNow()",
        ):
            self.assertIn(token, body)
        self.assertGreaterEqual(body.count("pendingInput = null"), 3)
        self.assertGreaterEqual(body.count("signal.notifyAll()"), 4)

    def test_capability_and_limits_are_truthfully_advertised(self) -> None:
        body = METADATA.read_text(encoding="utf-8")
        self.assertIn("supportsInteractiveInput = true", body)
        self.assertIn("maxInputPromptBytes = 4 * 1024", body)
        self.assertIn("maxInputReplyBytes = 64 * 1024", body)
        self.assertIn("maxInputPrompts = 128", body)
        self.assertIn("maxInputWaitMillis = 60_000L", body)

    def test_roadmap_contract_and_partial_gate_keep_evidence_boundaries_explicit(self) -> None:
        roadmap = ROADMAP.read_text(encoding="utf-8")
        contract = CONTRACT.read_text(encoding="utf-8")
        verifier = VERIFIER.read_text(encoding="utf-8")
        ignore = GITIGNORE.read_text(encoding="utf-8").splitlines()
        self.assertRegex(
            roadmap,
            re.compile(r"- \[x\] If interactive `input\(\)` is added, use execution-scoped"),
        )
        self.assertRegex(
            roadmap,
            re.compile(r"- \[x\] Bind input waits to cancellation, timeout, Binder death"),
        )
        self.assertIn("Protocol 1.3 extension", contract)
        for token in (
            "build/reports/python/u1/r2-interactive-input-contract.json",
            "CURRENT_TREE_R2_INTERACTIVE_INPUT_PARTIAL_FUNCTIONAL_GATE",
            "phaseStatus = 'PARTIAL'",
            "r2Complete = $false",
            "foregroundOnly = $hostScopedEvidencePassed",
            "backgroundUiForbidden = $hostScopedEvidencePassed",
            "typedPromptIds = $hostScopedEvidencePassed",
            "inputWaitLifecycleBound = $pluginFunctionalPassed",
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
        self.assertIn("!/tools/verify-u1-r2-interactive-input.ps1", ignore)

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
