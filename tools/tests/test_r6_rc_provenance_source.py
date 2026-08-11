from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
WRITER_PATH = REPO_ROOT / "tools" / "write-r6-rc-provenance.ps1"
WRITER = WRITER_PATH.read_text(encoding="utf-8")
VERIFIER = (REPO_ROOT / "tools" / "verify-r6-release-source.ps1").read_text(
    encoding="utf-8"
)
APP_BUILD = (REPO_ROOT / "app" / "build.gradle.kts").read_text(encoding="utf-8")
RELEASE_IDENTITY_LOCK = (
    REPO_ROOT / "locks" / "release-identity.lock"
).read_text(encoding="utf-8")
PINNED_KEYSTORE_SHA256 = (
    "0d6b79e4d4efe77829dbcc2e21096931ba7b0349df82f3b58c3e9d24e84f1df0"
)
PINNED_CERTIFICATE_SHA256 = (
    "31a681fcfffb3e428420cae280ded89292b12a3b0f59e19b7a73e32a8ae4c213"
)
HOST_API_IDS = (
    "common-plugin-api",
    "protocol-wire-api",
    "python-runtime-api",
)


def parse_properties(source: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw_line in source.splitlines():
        line = raw_line.strip()
        if not line or line.startswith(("#", "!")):
            continue
        key, separator, value = line.partition("=")
        if not separator or not key.strip() or key.strip() in result:
            raise ValueError("release identity lock is malformed or has duplicate keys")
        result[key.strip()] = value.strip()
    return result


def parse_claims(source: str) -> dict[str, object]:
    match = re.search(
        r"\$claims\s*=\s*\[ordered\]@\{(?P<body>.*?)^\}",
        source,
        flags=re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise ValueError("claims block missing")
    claims: dict[str, object] = {}
    for key, raw_value in re.findall(
        r"^\s*([A-Za-z][A-Za-z0-9]*)\s*=\s*('[^']*'|\$(?:true|false))\s*$",
        match.group("body"),
        flags=re.MULTILINE,
    ):
        if raw_value == "$true":
            value: object = True
        elif raw_value == "$false":
            value = False
        else:
            value = raw_value[1:-1]
        claims[key] = value
    return claims


def validate_local_candidate_claims(claims: dict[str, object]) -> None:
    expected = {
        "evidenceLevel": "RELEASE_CANDIDATE_LOCAL",
        "published": False,
        "deviceValidated": False,
        "p3Validated": False,
    }
    if claims != expected:
        raise ValueError("claims exceed the local Release Candidate evidence level")


class R6RcProvenanceSourceTest(unittest.TestCase):
    def test_all_artifact_and_tool_paths_are_explicit_mandatory_parameters(self) -> None:
        required = (
            "HostRepo",
            "HostApk",
            "PluginArm64Apk",
            "PluginX8664Apk",
            "PluginUniversalApk",
            "CommonPluginApiAar",
            "ProtocolWireApiAar",
            "PythonRuntimeApiAar",
            "Aapt2",
            "ApkSigner",
            "Output",
        )
        for name in required:
            pattern = (
                r"\[Parameter\(Mandatory\s*=\s*\$true\)\]"
                r"\s*\[ValidateNotNullOrEmpty\(\)\]"
                rf"\s*\[string\]\s*\${name}(?:,|\s*\))"
            )
            self.assertRegex(WRITER, pattern, name)

    def test_host_api_inventory_is_exactly_three_release_aars(self) -> None:
        verifier_ids_match = re.search(
            r"\$hostApiIds\s*=\s*@\((?P<body>.*?)\)",
            VERIFIER,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(verifier_ids_match)
        verifier_ids = tuple(
            re.findall(r"'([^']+)'", verifier_ids_match.group("body"))
        )
        writer_ids = tuple(
            re.findall(
                r"\[ordered\]@\{\s*id\s*=\s*'([^']+)';\s*path\s*=\s*\$[A-Za-z]+Aar\s*\}",
                WRITER,
            )
        )
        self.assertEqual(verifier_ids, HOST_API_IDS)
        self.assertEqual(writer_ids, HOST_API_IDS)
        exact_inventory_marker = (
            "Host API AAR lock inventory must contain exactly common-plugin-api, "
            "protocol-wire-api, and python-runtime-api file/SHA-256 pairs"
        )
        for source in (VERIFIER, WRITER):
            self.assertIn("$expectedHostApiLockKeys", source)
            self.assertIn("$unexpectedHostApiLockKeys", source)
            self.assertIn("$missingHostApiLockKeys", source)
            self.assertIn(exact_inventory_marker, source)
        self.assertIn(
            "Resolve-ExistingFile $CommonPluginApiAar 'Common Plugin API AAR'",
            WRITER,
        )

    def test_claims_are_exactly_local_candidate_and_negative_mutation_is_rejected(self) -> None:
        validate_local_candidate_claims(parse_claims(WRITER))
        hostile = WRITER.replace("published = $false", "published = $true", 1)
        with self.assertRaisesRegex(ValueError, "local Release Candidate"):
            validate_local_candidate_claims(parse_claims(hostile))

    def test_writer_is_secret_agnostic_and_has_atomic_ignored_output_contract(self) -> None:
        self.assertNotIn("sign.properties", WRITER.lower())
        self.assertNotRegex(WRITER.lower(), r"\badb(?:\.exe)?\b|gradlew")
        self.assertIn("build/reports", WRITER)
        self.assertIn("check-ignore", WRITER)
        self.assertIn("[IO.File]::Replace", WRITER)
        self.assertIn("[IO.File]::Move", WRITER)
        self.assertIn("[Guid]::NewGuid()", WRITER)

    def test_fail_closed_identity_and_artifact_markers_are_present(self) -> None:
        markers = (
            "Git worktree is not clean",
            "VERSION_BUILD must equal the clean repository commit count",
            "Host API AAR SHA-256 mismatch",
            "Python runtime canonical inventory SHA-256 mismatch",
            "signer set",
            "APK Signature Scheme v2",
            "application-debuggable",
            "Plugin universal APK ABI set",
        )
        for marker in markers:
            self.assertIn(marker, WRITER)

    def test_release_identity_lock_is_an_exact_source_contract(self) -> None:
        self.assertEqual(
            parse_properties(RELEASE_IDENTITY_LOCK),
            {
                "format": "1",
                "host.package": "org.autojs.autojs6",
                "plugin.package": (
                    "io.github.supermonster003.autojs6.plugin.python.runtime"
                ),
                "release.keystore.sha256": PINNED_KEYSTORE_SHA256,
                "release.certificate.sha256": PINNED_CERTIFICATE_SHA256,
            },
        )

    def test_gradle_and_source_gate_require_the_exact_keystore_bytes(self) -> None:
        for marker in (
            "locks/release-identity.lock",
            "releaseSigningStoreIsPinned",
            "storeFile.sha256() == lockedReleaseKeystoreSha256",
            PINNED_KEYSTORE_SHA256,
            PINNED_CERTIFICATE_SHA256,
        ):
            self.assertIn(marker, APP_BUILD)
            self.assertIn(marker, VERIFIER)
        self.assertIn("Get-Sha256 $storePath", VERIFIER)
        self.assertIn("Host API AAR lock identifies a dirty source tree", VERIFIER)
        self.assertIn("explicit clean Host HEAD identity", VERIFIER)

    def test_gradle_release_tasks_require_exact_host_distribution_provenance(self) -> None:
        for marker in (
            "expectedHostApiLockKeys",
            "releaseHostApiProvenanceReady",
            "Release artifact creation requires a clean Host HEAD",
            "collectReleaseFiles",
            "appendDigestToReleasedFiles",
        ):
            self.assertIn(marker, APP_BUILD)
        self.assertIn(
            "Host API AAR lock must contain exactly the three release AAR",
            APP_BUILD,
        )

    def test_stable_source_gate_requires_version_and_host_compatibility(self) -> None:
        self.assertIn(
            "VERSION_NAME must be exactly 0.1.0 for the stable source freeze",
            VERIFIER,
        )
        self.assertIn(
            "Python runtime metadata does not enforce the final Host 6.8.0",
            VERIFIER,
        )
        self.assertIn("PythonRuntimePluginInfoService", VERIFIER)

    def test_provenance_requires_four_singleton_pinned_signers_and_records_lock(self) -> None:
        self.assertIn("locks/release-identity.lock", WRITER)
        self.assertIn(PINNED_KEYSTORE_SHA256, WRITER)
        self.assertIn(PINNED_CERTIFICATE_SHA256, WRITER)
        self.assertIn("$allApkInfos = @($hostApkInfo", WRITER)
        self.assertIn("signer set is not an exact singleton", WRITER)
        self.assertIn("signer differs from the release identity pin", WRITER)
        self.assertIn("releaseIdentity = $releaseIdentityLockRecord", WRITER)


if __name__ == "__main__":
    unittest.main()
