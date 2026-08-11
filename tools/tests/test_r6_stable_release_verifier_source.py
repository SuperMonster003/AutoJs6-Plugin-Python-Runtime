from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER_PATH = REPO_ROOT / "tools" / "verify-r6-stable-release.ps1"
VERIFIER = VERIFIER_PATH.read_text(encoding="utf-8")
GITIGNORE = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")


class R6StableReleaseVerifierSourceTest(unittest.TestCase):
    def test_every_external_release_fact_is_a_mandatory_parameter(self) -> None:
        required = (
            "Provenance",
            "ProvenanceSha256",
            "P3Evidence",
            "P3EvidenceSha256",
            "ExpectedHostCommit",
            "ExpectedPluginCommit",
            "ResolvedTagCommit",
            "ReleaseTag",
            "ReleaseUrl",
            "ReleaseId",
            "ReleasePublishedAtUtc",
            "ReleaseDraft",
            "ReleasePrerelease",
            "LocalArm64Apk",
            "LocalX8664Apk",
            "LocalUniversalApk",
            "DownloadedArm64Apk",
            "DownloadedX8664Apk",
            "DownloadedUniversalApk",
            "RemoteArm64AssetName",
            "RemoteArm64Sha256",
            "RemoteArm64SizeBytes",
            "RemoteX8664AssetName",
            "RemoteX8664Sha256",
            "RemoteX8664SizeBytes",
            "RemoteUniversalAssetName",
            "RemoteUniversalSha256",
            "RemoteUniversalSizeBytes",
            "ExpectedDeviceSerial",
            "ExpectedDeviceApi",
            "ExpectedDeviceAbi",
            "ExpectedUserIds",
            "Aapt2",
            "ApkSigner",
            "Output",
        )
        for name in required:
            self.assertRegex(
                VERIFIER,
                rf"\[Parameter\(Mandatory\s*=\s*\$true\)\][\s\S]{{0,160}}?\${name}(?:,|\s*\n)",
                name,
            )

    def test_stable_source_and_release_identity_are_exact(self) -> None:
        markers = (
            "2caddcb763b39f0bf450909742fa6ec4caba27a8",
            "$pinnedHostVersionName = '6.8.0'",
            "$pinnedHostVersionCode = 5275L",
            "$pinnedPluginVersionName = '0.1.0'",
            "$pinnedPluginVersionCode = 11L",
            "Plugin commit count is not VERSION_BUILD 11",
            "P3 candidate versionCode is not 11",
            "[string[]] @('yyyy-MM-ddTHH:mm:ssZ', 'yyyy-MM-ddTHH:mm:ss.FFFFFFFZ')",
            "$provenanceCreatedAtValue -is [DateTime]",
            "$provenanceCreatedAtValue -is [DateTimeOffset]",
            "$pinnedReleaseTag = 'v0.1.0'",
            "https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/releases/tag/v0.1.0",
            "31a681fcfffb3e428420cae280ded89292b12a3b0f59e19b7a73e32a8ae4c213",
            "Resolved tag commit differs from the frozen plugin commit",
            "Remote arm64-v8a SHA-256",
            "local and downloaded APK bytes differ",
        )
        for marker in markers:
            self.assertIn(marker, VERIFIER)

    def test_three_host_api_aars_are_frozen_to_final_distribution(self) -> None:
        expected = {
            "common-plugin-api": "6d75eb2350aa56ed412dabf84b34c0f65b9a6f6cfce3f3c23f79b9b198c24a63",
            "protocol-wire-api": "e044dd3cc9bed84e844174e0963b57a1f67902cf021ccb42d1031d3511ce46da",
            "python-runtime-api": "e42a2c35cfb9bed27c02ad4a781a1b4bf7f5766d78a46ad194675f090c1c0127",
        }
        for artifact_id, sha256 in expected.items():
            self.assertIn(f"'{artifact_id}'", VERIFIER)
            self.assertIn(sha256, VERIFIER)
        self.assertIn(
            "9f296ad45c24b7eb3e217e4d0ce6c96ba2593966b2bed1db1f2846d658987818",
            VERIFIER,
        )
        self.assertIn("Host API AAR lock key inventory", VERIFIER)

    def test_p3_requires_exactly_fifteen_ordered_observations_and_restoration(self) -> None:
        self.assertIn("$observations.Count -eq 15", VERIFIER)
        indices = tuple(
            int(value)
            for value in re.findall(
                r"Assert-(?:Test|Phase)Observation \$observations\[(\d+)\]", VERIFIER
            )
        )
        self.assertEqual(indices, tuple(range(15)))
        markers = (
            "BASELINE_INSTALL",
            "BASELINE_TO_CANDIDATE_UPGRADE",
            "CANDIDATE_UNINSTALL_BASELINE_REINSTALL_ROLLBACK",
            "AVAILABLE_WITH_FRESH_APP_DATA",
            "VERIFIED_ABSENT_ALL_FROZEN_USERS_AND_GLOBAL",
            "INDEPENDENT_FINAL_RECEIPT_VERIFIER",
            "DECLARED_ABI_PACKAGING_AND_ACTUAL_DEVICE_COVERAGE_AGGREGATION",
        )
        for marker in markers:
            self.assertIn(marker, VERIFIER)

    def test_receipt_only_promotes_explicit_final_claims_and_coverage_boundary(self) -> None:
        claims_match = re.search(
            r"claims\s*=\s*\[ordered\]@\{(?P<body>.*?)^\s*\}",
            VERIFIER,
            flags=re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(claims_match)
        body = claims_match.group("body")
        self.assertIn("evidenceLevel = 'PRODUCTION_RELEASE'", body)
        self.assertIn("published = $true", body)
        self.assertIn("stableRelease = $true", body)
        self.assertIn("productionReleaseAuthorized = $true", body)
        self.assertIn("actualArm64", VERIFIER)
        self.assertIn("status = 'PACKAGING_ONLY'", VERIFIER)
        self.assertIn("x8664RuntimeDeviceEvidence = $false", VERIFIER)
        self.assertIn("runtimeTrustModel = 'TRUSTED_LOCAL_PYTHON_SCRIPTS_NON_SECURITY_SANDBOX'", VERIFIER)

    def test_tool_is_offline_atomic_and_version_controlled(self) -> None:
        forbidden = (
            r"(?i)\badb(?:\.exe)?\b",
            r"(?i)\bgradlew(?:\.bat)?\b",
            r"(?i)Invoke-WebRequest|Invoke-RestMethod",
            r"(?i)\bgh(?:\.exe)?\s",
        )
        for pattern in forbidden:
            self.assertNotRegex(VERIFIER, pattern)
        for marker in (
            "Output must be a file below the ignored plugin build/reports directory",
            "[Guid]::NewGuid()",
            "[IO.File]::WriteAllText",
            "[IO.File]::Replace",
            "[IO.File]::Move",
        ):
            self.assertIn(marker, VERIFIER)
        self.assertIn("!/tools/verify-r6-stable-release.ps1", GITIGNORE.splitlines())


if __name__ == "__main__":
    unittest.main()
