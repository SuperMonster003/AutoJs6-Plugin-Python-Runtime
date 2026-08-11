from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "runtime_lock_inventory_candidate.py"
SPEC = importlib.util.spec_from_file_location("runtime_lock_inventory_candidate", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class RuntimeLockInventoryCandidateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.lockfile = self.root / "gradle.lockfile"
        self.metadata = self.root / "verification-metadata.xml"
        self.artifact_root = self.root / "artifacts"
        self.artifact_root.mkdir()
        self._write_lockfile()
        self.contents = {
            key: f"verified bytes for {key[0]}|{key[1]}".encode("utf-8")
            for key in MODULE.EXPECTED_RUNTIME_ARTIFACTS
        }
        self._write_metadata()
        self.paths = self._write_artifacts()

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def _write_lockfile(self, extra_coordinate: str | None = None) -> None:
        lines = [
            "# This is a Gradle generated file for dependency locking.",
            "# This file is expected to be part of source control.",
            "org.jetbrains.kotlin:kotlin-stdlib:2.2.21=debugRuntimeClasspath",
        ]
        if extra_coordinate:
            lines.append(f"{extra_coordinate}=debugRuntimeClasspath")
        self.lockfile.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _write_metadata(
        self,
        *,
        extra_runtime_artifact: tuple[str, str, bytes] | None = None,
        coordinate_replacement: tuple[str, str] | None = None,
    ) -> None:
        by_coordinate: dict[str, list[tuple[str, bytes]]] = {}
        for key, content in self.contents.items():
            coordinate, file_name = key
            if coordinate_replacement and coordinate == coordinate_replacement[0]:
                coordinate = coordinate_replacement[1]
            by_coordinate.setdefault(coordinate, []).append((file_name, content))
        if extra_runtime_artifact:
            coordinate, file_name, content = extra_runtime_artifact
            by_coordinate.setdefault(coordinate, []).append((file_name, content))

        component_xml = [
            '<component group="com.chaquo.python" name="com.chaquo.python.gradle.plugin" version="17.0.0">'
            '<artifact name="com.chaquo.python.gradle.plugin-17.0.0.pom">'
            f'<sha256 value="{hashlib.sha256(b"plugin pom").hexdigest()}"/>'
            '</artifact></component>',
            '<component group="com.chaquo.python" name="gradle" version="17.0.0">'
            '<artifact name="gradle-17.0.0.jar">'
            f'<sha256 value="{hashlib.sha256(b"plugin jar").hexdigest()}"/>'
            '</artifact><artifact name="gradle-17.0.0.module">'
            f'<sha256 value="{hashlib.sha256(b"plugin module").hexdigest()}"/>'
            '</artifact></component>',
        ]
        for coordinate, entries in by_coordinate.items():
            group, name, version = coordinate.split(":")
            artifacts = []
            for file_name, content in entries:
                artifacts.append(
                    f'<artifact name="{file_name}"><sha256 value="{hashlib.sha256(content).hexdigest()}"/></artifact>'
                )
            metadata_name = f"{name}-{version}.pom"
            artifacts.append(
                f'<artifact name="{metadata_name}"><sha256 value="{hashlib.sha256(metadata_name.encode()).hexdigest()}"/></artifact>'
            )
            component_xml.append(
                f'<component group="{group}" name="{name}" version="{version}">'
                + "".join(artifacts)
                + "</component>"
            )
        self.metadata.write_text(
            '<verification-metadata xmlns="https://schema.gradle.org/dependency-verification">'
            '<components>'
            + "".join(component_xml)
            + '</components></verification-metadata>',
            encoding="utf-8",
        )

    def _write_artifacts(self) -> dict[tuple[str, str], Path]:
        paths = {}
        for key, content in self.contents.items():
            coordinate, file_name = key
            path = self.artifact_root / coordinate.replace(":", "_") / file_name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            paths[key] = path
        return paths

    def _evidence_and_inventory(self):
        lock_evidence = MODULE.parse_gradle_lock_evidence(self.lockfile)
        metadata_evidence = MODULE.parse_verification_metadata(self.metadata)
        discovered, explicit = MODULE.discover_artifacts(
            [],
            [self.artifact_root],
            frozenset(file_name for _, file_name in MODULE.EXPECTED_RUNTIME_ARTIFACTS),
        )
        records = MODULE.build_inventory(
            metadata_evidence.artifact_hashes, discovered, explicit
        )
        return lock_evidence, metadata_evidence, records

    def test_generates_exact_nine_artifact_properties_and_json_candidates(self) -> None:
        lock_evidence, metadata_evidence, records = self._evidence_and_inventory()
        self.assertEqual(9, len(records))
        self.assertEqual(1, lock_evidence.ordinary_coordinate_count)
        self.assertEqual(2, metadata_evidence.filtered_build_plugin_components)
        self.assertEqual(3, metadata_evidence.filtered_build_plugin_artifacts)
        self.assertEqual(5, metadata_evidence.filtered_runtime_metadata_artifacts)
        properties = MODULE.render_properties(records, lock_evidence, metadata_evidence)
        self.assertIn("runtime.artifacts.count=9", properties)
        self.assertIn("plugin-managed and absent from app/gradle.lockfile", properties)
        document = MODULE.candidate_document(records, lock_evidence, metadata_evidence)
        self.assertEqual("REVIEW_CANDIDATE_ONLY", document["trust"])
        self.assertFalse(
            document["gradleDependencyLock"]["pluginManagedRuntimeCoordinatesPresent"]
        )
        self.assertEqual(["arm64-v8a", "x86_64"], document["runtimeContract"]["abis"])
        self.assertEqual(9, len(document["artifacts"]))

        properties_path = self.root / "candidate.properties"
        properties_path.write_text(properties, encoding="utf-8")
        MODULE.verify_candidate(
            properties_path,
            "properties",
            records,
            lock_evidence,
            metadata_evidence,
        )
        json_path = self.root / "candidate.json"
        json_path.write_text(MODULE.render_json(document), encoding="utf-8")
        MODULE.verify_candidate(
            json_path, "json", records, lock_evidence, metadata_evidence
        )

    def test_rejects_plugin_managed_runtime_in_gradle_lock(self) -> None:
        self._write_lockfile("com.chaquo.python:target:3.13.9-0")
        with self.assertRaisesRegex(MODULE.InventoryError, "(?i)plugin-managed"):
            MODULE.parse_gradle_lock_evidence(self.lockfile)

    def test_rejects_missing_cache_artifact(self) -> None:
        self.paths[MODULE.EXPECTED_RUNTIME_ARTIFACTS[-1]].unlink()
        lock_evidence = MODULE.parse_gradle_lock_evidence(self.lockfile)
        metadata_evidence = MODULE.parse_verification_metadata(self.metadata)
        discovered, explicit = MODULE.discover_artifacts(
            [],
            [self.artifact_root],
            frozenset(file_name for _, file_name in MODULE.EXPECTED_RUNTIME_ARTIFACTS),
        )
        self.assertIsNotNone(lock_evidence)
        with self.assertRaisesRegex(MODULE.InventoryError, "Missing cache bytes"):
            MODULE.build_inventory(
                metadata_evidence.artifact_hashes, discovered, explicit
            )

    def test_rejects_explicit_artifact_with_wrong_bytes(self) -> None:
        path = self.paths[MODULE.EXPECTED_RUNTIME_ARTIFACTS[0]]
        path.write_bytes(b"tampered")
        metadata_evidence = MODULE.parse_verification_metadata(self.metadata)
        discovered, explicit = MODULE.discover_artifacts(
            [path],
            [],
            frozenset(file_name for _, file_name in MODULE.EXPECTED_RUNTIME_ARTIFACTS),
        )
        with self.assertRaisesRegex(MODULE.InventoryError, "Missing cache bytes"):
            MODULE.build_inventory(
                metadata_evidence.artifact_hashes, discovered, explicit
            )

    def test_rejects_extra_runtime_binary_in_metadata(self) -> None:
        coordinate = MODULE.EXPECTED_RUNTIME_ARTIFACTS[3][0]
        self._write_metadata(
            extra_runtime_artifact=(coordinate, "bootstrap-17.0.0-3.13-extra.imy", b"extra")
        )
        with self.assertRaisesRegex(MODULE.InventoryError, "Unexpected runtime artifact"):
            MODULE.parse_verification_metadata(self.metadata)

    def test_rejects_wrong_runtime_component_version(self) -> None:
        old_coordinate = MODULE.EXPECTED_RUNTIME_ARTIFACTS[3][0]
        self._write_metadata(
            coordinate_replacement=(
                old_coordinate,
                "com.chaquo.python.runtime:bootstrap:17.0.1",
            )
        )
        with self.assertRaisesRegex(MODULE.InventoryError, "Unexpected Chaquopy component"):
            MODULE.parse_verification_metadata(self.metadata)

    def test_rejects_wrong_abi_runtime_artifact(self) -> None:
        coordinate = MODULE.EXPECTED_RUNTIME_ARTIFACTS[4][0]
        self._write_metadata(
            extra_runtime_artifact=(
                coordinate,
                "chaquopy-17.0.0-3.13-armeabi-v7a.so",
                b"wrong abi",
            )
        )
        with self.assertRaisesRegex(MODULE.InventoryError, "Unexpected runtime artifact"):
            MODULE.parse_verification_metadata(self.metadata)

    def test_rejects_changed_json_candidate(self) -> None:
        lock_evidence, metadata_evidence, records = self._evidence_and_inventory()
        document = MODULE.candidate_document(records, lock_evidence, metadata_evidence)
        document["artifacts"][0]["sha256"] = "0" * 64
        path = self.root / "changed.json"
        path.write_text(json.dumps(document), encoding="utf-8")
        with self.assertRaisesRegex(MODULE.InventoryError, "does not exactly match"):
            MODULE.verify_candidate(
                path, "json", records, lock_evidence, metadata_evidence
            )

    def test_rejects_one_cache_file_matching_two_runtime_identities(self) -> None:
        shared = self.root / "shared.so"
        shared.write_bytes(b"shared")
        shared_hash = hashlib.sha256(b"shared").hexdigest()
        expected = {
            (f"group:item-{index}:1", "shared.so" if index < 2 else f"item-{index}.bin"): (
                shared_hash if index < 2 else hashlib.sha256(str(index).encode()).hexdigest()
            )
            for index in range(9)
        }
        files = [shared]
        for index in range(2, 9):
            path = self.root / f"item-{index}.bin"
            path.write_bytes(str(index).encode())
            files.append(path)
        with self.assertRaisesRegex(MODULE.InventoryError, "ambiguously matches"):
            MODULE.build_inventory(expected, files, files)

    def test_rejects_metadata_dtd(self) -> None:
        self.metadata.write_text(
            '<!DOCTYPE x [<!ENTITY y "z">]><verification-metadata/>',
            encoding="utf-8",
        )
        with self.assertRaisesRegex(MODULE.InventoryError, "DTD or entity"):
            MODULE.parse_verification_metadata(self.metadata)

    def test_generator_source_has_no_write_or_process_capability(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        forbidden = (
            "write_text(",
            "write_bytes(",
            "subprocess",
            "os.system",
            "Popen(",
            "adb ",
            "gradlew",
        )
        for marker in forbidden:
            self.assertNotIn(marker, source)


if __name__ == "__main__":
    unittest.main()
