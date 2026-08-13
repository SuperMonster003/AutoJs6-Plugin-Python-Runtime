from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools" / "verify-u1-r1-core-semantics.ps1"
ROADMAP = ROOT / "ROADMAP.md"
GITIGNORE = ROOT / ".gitignore"


class U1R1CoreSemanticsGateSourceTest(unittest.TestCase):
    def test_verifier_has_exact_portable_plugin_and_optional_host_steps(self) -> None:
        body = VERIFIER.read_text(encoding="utf-8")
        for token in (
            "tools/tests",
            "test_*.py",
            ":app:testDebugUnitTest",
            ":app:assembleDebug",
            "HostRepository",
            ":plugin-api:python-runtime-api:test",
            ":app:testAppDebugUnitTest",
            ":app:compileAppDebugKotlin",
        ):
            self.assertIn(token, body)
        self.assertNotRegex(
            body.lower(),
            r"\badb(?:\.exe)?\b|connected[a-z]*test|instrumentation|install(?:debug|release)",
        )

    def test_report_is_atomic_and_cannot_claim_device_or_release_evidence(self) -> None:
        body = VERIFIER.read_text(encoding="utf-8")
        self.assertIn("build/reports/python/u1/r1-core-semantics-gate.json", body)
        self.assertIn("PORTABLE_CPYTHON_ONLY", body)
        self.assertIn("ANDROID_BUILD_ONLY", body)
        self.assertRegex(body, r"binderExecuted\s*=\s*\$false")
        self.assertRegex(body, r"deviceVerified\s*=\s*\$false")
        self.assertRegex(body, r"productionEvidence\s*=\s*\$false")
        self.assertRegex(body, r"published\s*=\s*\$false")
        self.assertRegex(body, r"releaseAuthorized\s*=\s*\$false")
        self.assertIn('$temporaryPath = "$reportPath.tmp"', body)
        self.assertIn("Move-Item -LiteralPath $temporaryPath -Destination $reportPath -Force", body)

    def test_roadmap_and_ignore_rules_expose_the_tracked_gate(self) -> None:
        roadmap = ROADMAP.read_text(encoding="utf-8")
        ignore = GITIGNORE.read_text(encoding="utf-8")
        self.assertIn("tools\\verify-u1-r1-core-semantics.ps1", roadmap)
        self.assertIn("build/reports/python/u1/r1-core-semantics-gate.json", roadmap)
        self.assertIn("-HostRepository D:\\idea-projects\\AutoJs6", roadmap)
        self.assertIn("!/tools/verify-u1-r1-core-semantics.ps1", ignore.splitlines())

    def test_verifier_contains_no_publication_mutation_command(self) -> None:
        body = VERIFIER.read_text(encoding="utf-8").lower()
        self.assertNotRegex(
            body,
            r"\bgh\b|git\s+(?:commit|push|tag)|verify-r6|publish(?:plugin|release|bundle)",
        )


if __name__ == "__main__":
    unittest.main()
