#!/usr/bin/env python3
"""Build or verify a review-only Chaquopy runtime lock candidate.

Chaquopy resolves its packaged runtime artifacts outside Gradle dependency
locking. Therefore app/gradle.lockfile is checked as non-empty ordinary-lock
evidence and must contain no Chaquopy runtime coordinate. The exact runtime
files instead come from Gradle verification metadata and matching cache bytes.

The program is deliberately read-only. It never edits either Gradle metadata
file or locks/python-runtime.lock, and it never launches another process.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
SHA256_HEX_LENGTH = 64
CHAQUOPY_GROUP_PREFIX = "com.chaquo.python"
CHAQUOPY_VERSION = "17.0.0"
PYTHON_RUNTIME_VERSION = "3.13.9-0"
PYTHON_LINE = "3.13"
SUPPORTED_ABIS = ("arm64-v8a", "x86_64")
CANDIDATE_SCHEMA = "autojs6-python-runtime-lock-candidate-v1"

# Order is part of the canonical candidate contract.
EXPECTED_RUNTIME_ARTIFACTS = (
    (
        f"com.chaquo.python:target:{PYTHON_RUNTIME_VERSION}",
        f"target-{PYTHON_RUNTIME_VERSION}-arm64-v8a.zip",
    ),
    (
        f"com.chaquo.python:target:{PYTHON_RUNTIME_VERSION}",
        f"target-{PYTHON_RUNTIME_VERSION}-stdlib-pyc.zip",
    ),
    (
        f"com.chaquo.python:target:{PYTHON_RUNTIME_VERSION}",
        f"target-{PYTHON_RUNTIME_VERSION}-x86_64.zip",
    ),
    (
        f"com.chaquo.python.runtime:bootstrap:{CHAQUOPY_VERSION}",
        f"bootstrap-{CHAQUOPY_VERSION}-{PYTHON_LINE}.imy",
    ),
    (
        f"com.chaquo.python.runtime:chaquopy:{CHAQUOPY_VERSION}",
        f"chaquopy-{CHAQUOPY_VERSION}-{PYTHON_LINE}-arm64-v8a.so",
    ),
    (
        f"com.chaquo.python.runtime:chaquopy:{CHAQUOPY_VERSION}",
        f"chaquopy-{CHAQUOPY_VERSION}-{PYTHON_LINE}-x86_64.so",
    ),
    (
        f"com.chaquo.python.runtime:chaquopy_java:{CHAQUOPY_VERSION}",
        f"chaquopy_java-{CHAQUOPY_VERSION}.jar",
    ),
    (
        f"com.chaquo.python.runtime:libchaquopy_java:{CHAQUOPY_VERSION}",
        f"libchaquopy_java-{CHAQUOPY_VERSION}-{PYTHON_LINE}-arm64-v8a.so",
    ),
    (
        f"com.chaquo.python.runtime:libchaquopy_java:{CHAQUOPY_VERSION}",
        f"libchaquopy_java-{CHAQUOPY_VERSION}-{PYTHON_LINE}-x86_64.so",
    ),
)
EXPECTED_RUNTIME_COMPONENTS = frozenset(
    coordinate for coordinate, _ in EXPECTED_RUNTIME_ARTIFACTS
)
FILTERED_BUILD_PLUGIN_COMPONENTS = frozenset(
    {
        f"com.chaquo.python:com.chaquo.python.gradle.plugin:{CHAQUOPY_VERSION}",
        f"com.chaquo.python:gradle:{CHAQUOPY_VERSION}",
    }
)
FILTERED_METADATA_SUFFIXES = (".pom", ".module")


class InventoryError(ValueError):
    """Raised when evidence cannot form the exact nine-file runtime inventory."""


@dataclass(frozen=True)
class GradleLockEvidence:
    sha256: str
    ordinary_coordinate_count: int


@dataclass(frozen=True)
class VerificationMetadataEvidence:
    sha256: str
    artifact_hashes: Mapping[tuple[str, str], str]
    filtered_build_plugin_components: int
    filtered_build_plugin_artifacts: int
    filtered_runtime_metadata_artifacts: int


@dataclass(frozen=True)
class ArtifactRecord:
    coordinate: str
    file_name: str
    sha256: str


def _read_bytes(path: Path, label: str) -> bytes:
    if not path.is_file():
        raise InventoryError(f"Missing {label}: {path}")
    return path.read_bytes()


def _read_text(path: Path, label: str) -> str:
    try:
        return _read_bytes(path, label).decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise InventoryError(f"{label} is not UTF-8: {path}") from error


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _is_sha256(value: str) -> bool:
    return len(value) == SHA256_HEX_LENGTH and all(
        character in "0123456789abcdef" for character in value
    )


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_gradle_lock_evidence(lockfile: Path) -> GradleLockEvidence:
    content = _read_bytes(lockfile, "Gradle lockfile")
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise InventoryError(f"Gradle lockfile is not UTF-8: {lockfile}") from error
    if "This is a Gradle generated file for dependency locking" not in text:
        raise InventoryError("Gradle lockfile lacks its generated-file marker")

    coordinates: set[str] = set()
    seen_keys: set[str] = set()
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith(("#", "!")):
            continue
        if "=" not in line:
            raise InventoryError(
                f"Malformed Gradle lockfile line {line_number}: missing '='"
            )
        key = line.split("=", 1)[0].strip()
        if not key:
            raise InventoryError(f"Empty Gradle lock key at line {line_number}")
        if key in seen_keys:
            raise InventoryError(f"Duplicate Gradle lock key: {key}")
        seen_keys.add(key)
        if key == "empty":
            continue
        parts = key.split(":")
        if len(parts) != 3 or any(not part for part in parts):
            raise InventoryError(f"Unsupported Gradle module coordinate: {key}")
        coordinates.add(key)

    if not coordinates:
        raise InventoryError("Gradle lockfile contains no ordinary dependency coordinates")
    plugin_managed = sorted(
        coordinate
        for coordinate in coordinates
        if coordinate.split(":", 1)[0].startswith(CHAQUOPY_GROUP_PREFIX)
    )
    if plugin_managed:
        raise InventoryError(
            "Plugin-managed Chaquopy runtime unexpectedly entered app/gradle.lockfile: "
            + ", ".join(plugin_managed)
        )
    return GradleLockEvidence(_sha256_bytes(content), len(coordinates))


def _artifact_sha256(artifact: ET.Element, coordinate: str, file_name: str) -> str:
    hashes = {
        node.attrib.get("value", "").strip().lower()
        for node in artifact.iter()
        if _local_name(node.tag) == "sha256"
    }
    if len(hashes) != 1 or not _is_sha256(next(iter(hashes), "")):
        raise InventoryError(
            f"Artifact lacks one exact verification SHA-256: {coordinate}|{file_name}"
        )
    return next(iter(hashes))


def parse_verification_metadata(metadata_file: Path) -> VerificationMetadataEvidence:
    xml_bytes = _read_bytes(metadata_file, "verification metadata")
    upper_xml = xml_bytes.upper()
    if b"<!DOCTYPE" in upper_xml or b"<!ENTITY" in upper_xml:
        raise InventoryError("Verification metadata must not contain a DTD or entity")
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as error:
        raise InventoryError(f"Malformed verification metadata: {error}") from error

    runtime_artifacts: dict[tuple[str, str], str] = {}
    seen_components: set[str] = set()
    filtered_build_components = 0
    filtered_build_artifacts = 0
    filtered_runtime_metadata = 0
    for component in root.iter():
        if _local_name(component.tag) != "component":
            continue
        group = component.attrib.get("group", "")
        if not group.startswith(CHAQUOPY_GROUP_PREFIX):
            continue
        coordinate = ":".join(
            component.attrib.get(attribute, "")
            for attribute in ("group", "name", "version")
        )
        if coordinate in seen_components:
            raise InventoryError(f"Duplicate Chaquopy verification component: {coordinate}")
        seen_components.add(coordinate)

        artifacts = [
            child for child in component if _local_name(child.tag) == "artifact"
        ]
        if coordinate in FILTERED_BUILD_PLUGIN_COMPONENTS:
            filtered_build_components += 1
            filtered_build_artifacts += len(artifacts)
            continue
        if coordinate not in EXPECTED_RUNTIME_COMPONENTS:
            raise InventoryError(
                f"Unexpected Chaquopy component or version in verification metadata: {coordinate}"
            )

        expected_names = {
            file_name
            for expected_coordinate, file_name in EXPECTED_RUNTIME_ARTIFACTS
            if expected_coordinate == coordinate
        }
        for artifact in artifacts:
            file_name = artifact.attrib.get("name", "").strip()
            if (
                not file_name
                or file_name != Path(file_name).name
                or "/" in file_name
                or "\\" in file_name
                or "|" in file_name
            ):
                raise InventoryError(
                    f"Invalid verification metadata artifact name for {coordinate}: {file_name!r}"
                )
            if file_name.endswith(FILTERED_METADATA_SUFFIXES):
                filtered_runtime_metadata += 1
                continue
            if file_name not in expected_names:
                raise InventoryError(
                    f"Unexpected runtime artifact for {coordinate}: {file_name}"
                )
            key = (coordinate, file_name)
            if key in runtime_artifacts:
                raise InventoryError(
                    f"Duplicate runtime artifact in verification metadata: {coordinate}|{file_name}"
                )
            runtime_artifacts[key] = _artifact_sha256(
                artifact, coordinate, file_name
            )

    missing_components = sorted(EXPECTED_RUNTIME_COMPONENTS - seen_components)
    if missing_components:
        raise InventoryError(
            "Missing runtime verification component(s): " + ", ".join(missing_components)
        )
    expected_keys = set(EXPECTED_RUNTIME_ARTIFACTS)
    actual_keys = set(runtime_artifacts)
    if actual_keys != expected_keys:
        missing = sorted(expected_keys - actual_keys)
        extra = sorted(actual_keys - expected_keys)
        details = []
        if missing:
            details.append(
                "missing=" + ",".join(f"{c}|{f}" for c, f in missing)
            )
        if extra:
            details.append("extra=" + ",".join(f"{c}|{f}" for c, f in extra))
        raise InventoryError("Runtime verification artifact set mismatch: " + "; ".join(details))

    ordered_hashes = {
        key: runtime_artifacts[key] for key in EXPECTED_RUNTIME_ARTIFACTS
    }
    return VerificationMetadataEvidence(
        sha256=_sha256_bytes(xml_bytes),
        artifact_hashes=ordered_hashes,
        filtered_build_plugin_components=filtered_build_components,
        filtered_build_plugin_artifacts=filtered_build_artifacts,
        filtered_runtime_metadata_artifacts=filtered_runtime_metadata,
    )


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _resolved_file(path: Path, label: str) -> Path:
    if path.is_symlink():
        raise InventoryError(f"{label} must not be a symbolic link: {path}")
    if not path.is_file():
        raise InventoryError(f"Missing {label}: {path}")
    return path.resolve()


def discover_artifacts(
    artifact_files: Sequence[Path],
    artifact_roots: Sequence[Path],
    wanted_names: frozenset[str],
) -> tuple[frozenset[Path], frozenset[Path]]:
    discovered: set[Path] = set()
    explicit: set[Path] = set()
    for artifact in artifact_files:
        resolved = _resolved_file(artifact, "resolved artifact")
        if resolved.name not in wanted_names:
            raise InventoryError(
                f"Explicit artifact is outside the exact runtime contract: {resolved}"
            )
        explicit.add(resolved)
        discovered.add(resolved)

    for root in artifact_roots:
        if root.is_symlink():
            raise InventoryError(f"Artifact root must not be a symbolic link: {root}")
        if not root.is_dir():
            raise InventoryError(f"Missing artifact root: {root}")
        for directory, child_directories, file_names in os.walk(root, followlinks=False):
            child_directories[:] = [
                name
                for name in child_directories
                if not (Path(directory) / name).is_symlink()
            ]
            for file_name in file_names:
                if file_name in wanted_names:
                    candidate = Path(directory) / file_name
                    if not candidate.is_symlink() and candidate.is_file():
                        discovered.add(candidate.resolve())

    if not discovered:
        raise InventoryError("No exact runtime artifact files were supplied or discovered")
    return frozenset(discovered), frozenset(explicit)


def build_inventory(
    expected: Mapping[tuple[str, str], str],
    discovered_files: Iterable[Path],
    explicit_files: Iterable[Path],
) -> tuple[ArtifactRecord, ...]:
    files_by_name: dict[str, list[tuple[Path, str]]] = {}
    hashes_by_path: dict[Path, str] = {}
    for path in sorted(set(discovered_files), key=str):
        actual_hash = _sha256_file(path)
        hashes_by_path[path] = actual_hash
        files_by_name.setdefault(path.name, []).append((path, actual_hash))

    records: list[ArtifactRecord] = []
    matched_paths: set[Path] = set()
    path_identities: dict[Path, set[tuple[str, str]]] = {}
    for (coordinate, file_name), expected_hash in expected.items():
        matching = [
            path
            for path, actual_hash in files_by_name.get(file_name, [])
            if actual_hash == expected_hash
        ]
        if not matching:
            raise InventoryError(
                "Missing cache bytes matching verification metadata: "
                f"{coordinate}|{file_name}|{expected_hash}"
            )
        records.append(ArtifactRecord(coordinate, file_name, expected_hash))
        for path in matching:
            matched_paths.add(path)
            path_identities.setdefault(path, set()).add((coordinate, file_name))

    ambiguous_paths = sorted(
        (path, identities)
        for path, identities in path_identities.items()
        if len(identities) > 1
    )
    if ambiguous_paths:
        path, identities = ambiguous_paths[0]
        raise InventoryError(
            f"One cache file ambiguously matches multiple runtime identities: {path}: "
            + ", ".join(f"{coordinate}|{name}" for coordinate, name in sorted(identities))
        )

    unmatched_explicit = sorted(set(explicit_files) - matched_paths, key=str)
    if unmatched_explicit:
        path = unmatched_explicit[0]
        raise InventoryError(
            f"Explicit artifact bytes do not match verification metadata: "
            f"{path} ({hashes_by_path[path]})"
        )
    if len(records) != len(EXPECTED_RUNTIME_ARTIFACTS):
        raise InventoryError(
            f"Runtime inventory must contain exactly {len(EXPECTED_RUNTIME_ARTIFACTS)} artifacts"
        )
    return tuple(records)


def canonical_inventory(records: Sequence[ArtifactRecord]) -> str:
    return "".join(
        f"{index:03d}|{record.coordinate}|{record.file_name}|{record.sha256}\n"
        for index, record in enumerate(records)
    )


def candidate_values(records: Sequence[ArtifactRecord]) -> dict[str, str]:
    canonical = canonical_inventory(records)
    values = {
        "runtime.artifacts.state": "RESOLVED",
        "runtime.artifacts.count": str(len(records)),
    }
    for index, record in enumerate(records):
        prefix = f"runtime.artifact.{index:03d}"
        values[f"{prefix}.coordinate"] = record.coordinate
        values[f"{prefix}.file"] = record.file_name
        values[f"{prefix}.sha256"] = record.sha256
    values["runtime.artifacts.inventory.sha256"] = _sha256_bytes(
        canonical.encode("utf-8")
    )
    return values


def candidate_document(
    records: Sequence[ArtifactRecord],
    lock_evidence: GradleLockEvidence,
    metadata_evidence: VerificationMetadataEvidence,
) -> dict[str, object]:
    canonical = canonical_inventory(records)
    return {
        "schema": CANDIDATE_SCHEMA,
        "trust": "REVIEW_CANDIDATE_ONLY",
        "gradleDependencyLock": {
            "path": "app/gradle.lockfile",
            "sha256": lock_evidence.sha256,
            "ordinaryCoordinateCount": lock_evidence.ordinary_coordinate_count,
            "pluginManagedRuntimeCoordinatesPresent": False,
            "role": "ORDINARY_DEPENDENCY_LOCK_EVIDENCE_ONLY",
        },
        "verificationMetadata": {
            "path": "gradle/verification-metadata.xml",
            "sha256": metadata_evidence.sha256,
            "role": "PLUGIN_MANAGED_RUNTIME_SHA256_SOURCE",
            "filteredBuildPluginComponents": metadata_evidence.filtered_build_plugin_components,
            "filteredBuildPluginArtifacts": metadata_evidence.filtered_build_plugin_artifacts,
            "filteredRuntimePomOrModuleArtifacts": metadata_evidence.filtered_runtime_metadata_artifacts,
        },
        "runtimeContract": {
            "chaquopyVersion": CHAQUOPY_VERSION,
            "pythonRuntimeVersion": PYTHON_RUNTIME_VERSION,
            "pythonLine": PYTHON_LINE,
            "abis": list(SUPPORTED_ABIS),
            "componentCount": len(EXPECTED_RUNTIME_COMPONENTS),
            "artifactCount": len(EXPECTED_RUNTIME_ARTIFACTS),
        },
        "artifacts": [
            {
                "ordinal": f"{index:03d}",
                "coordinate": record.coordinate,
                "file": record.file_name,
                "sha256": record.sha256,
            }
            for index, record in enumerate(records)
        ],
        "canonicalInventory": canonical,
        "canonicalInventorySha256": _sha256_bytes(canonical.encode("utf-8")),
    }


def render_properties(
    records: Sequence[ArtifactRecord],
    lock_evidence: GradleLockEvidence,
    metadata_evidence: VerificationMetadataEvidence,
) -> str:
    values = candidate_values(records)
    lines = [
        "# REVIEW CANDIDATE ONLY - NOT A TRUST DECISION",
        "# Chaquopy runtime is plugin-managed and absent from app/gradle.lockfile.",
        f"# app.gradle.lockfile.sha256={lock_evidence.sha256}",
        f"# app.gradle.lockfile.ordinary.coordinates={lock_evidence.ordinary_coordinate_count}",
        f"# verification.metadata.sha256={metadata_evidence.sha256}",
        f"runtime.artifacts.state={values['runtime.artifacts.state']}",
        f"runtime.artifacts.count={values['runtime.artifacts.count']}",
    ]
    for index in range(len(records)):
        prefix = f"runtime.artifact.{index:03d}"
        lines.extend(
            [
                f"{prefix}.coordinate={values[f'{prefix}.coordinate']}",
                f"{prefix}.file={values[f'{prefix}.file']}",
                f"{prefix}.sha256={values[f'{prefix}.sha256']}",
            ]
        )
    lines.append(
        "runtime.artifacts.inventory.sha256="
        + values["runtime.artifacts.inventory.sha256"]
    )
    return "\n".join(lines) + "\n"


def render_json(document: Mapping[str, object]) -> str:
    return json.dumps(document, ensure_ascii=False, indent=2) + "\n"


def _unique_json_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise InventoryError(f"Duplicate JSON candidate key: {key}")
        result[key] = value
    return result


def parse_properties_candidate(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line_number, raw_line in enumerate(
        _read_text(path, "candidate inventory").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line or line.startswith(("#", "!")):
            continue
        if "=" not in line:
            raise InventoryError(f"Malformed candidate line {line_number}")
        key, value = (part.strip() for part in line.split("=", 1))
        if not key or not value:
            raise InventoryError(f"Empty candidate key or value at line {line_number}")
        if key in values:
            raise InventoryError(f"Duplicate candidate key: {key}")
        values[key] = value
    return values


def verify_candidate(
    path: Path,
    candidate_format: str,
    records: Sequence[ArtifactRecord],
    lock_evidence: GradleLockEvidence,
    metadata_evidence: VerificationMetadataEvidence,
) -> None:
    if candidate_format == "json":
        try:
            actual = json.loads(
                _read_text(path, "JSON candidate"),
                object_pairs_hook=_unique_json_object,
            )
        except json.JSONDecodeError as error:
            raise InventoryError(f"Malformed JSON candidate: {error}") from error
        expected: object = candidate_document(records, lock_evidence, metadata_evidence)
    else:
        actual = parse_properties_candidate(path)
        expected = candidate_values(records)
    if actual != expected:
        raise InventoryError(
            "Candidate does not exactly match current lock, metadata, and cache bytes"
        )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--lockfile",
        type=Path,
        default=REPO_ROOT / "app" / "gradle.lockfile",
    )
    parser.add_argument(
        "--verification-metadata",
        type=Path,
        default=REPO_ROOT / "gradle" / "verification-metadata.xml",
    )
    parser.add_argument(
        "--artifact",
        action="append",
        type=Path,
        default=[],
        help="Exact resolved runtime artifact file; repeat as needed.",
    )
    parser.add_argument(
        "--artifact-root",
        action="append",
        type=Path,
        default=[],
        help="Read-only recursive root containing resolved artifacts; repeat as needed.",
    )
    parser.add_argument(
        "--format",
        choices=("properties", "json"),
        default="properties",
    )
    parser.add_argument(
        "--verify-candidate",
        type=Path,
        help="Read and verify a captured candidate instead of rendering it.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    if not args.artifact and not args.artifact_root:
        parser.error("at least one --artifact or --artifact-root is required")
    try:
        lock_evidence = parse_gradle_lock_evidence(args.lockfile)
        metadata_evidence = parse_verification_metadata(args.verification_metadata)
        discovered, explicit = discover_artifacts(
            args.artifact,
            args.artifact_root,
            frozenset(file_name for _, file_name in EXPECTED_RUNTIME_ARTIFACTS),
        )
        records = build_inventory(
            metadata_evidence.artifact_hashes, discovered, explicit
        )
        if args.verify_candidate:
            verify_candidate(
                args.verify_candidate,
                args.format,
                records,
                lock_evidence,
                metadata_evidence,
            )
            print("RUNTIME_LOCK_INVENTORY_CANDIDATE=VERIFIED")
            print(f"ARTIFACT_COUNT={len(records)}")
            print(
                "CANONICAL_INVENTORY_SHA256="
                + candidate_values(records)["runtime.artifacts.inventory.sha256"]
            )
        elif args.format == "json":
            sys.stdout.write(
                render_json(
                    candidate_document(records, lock_evidence, metadata_evidence)
                )
            )
        else:
            sys.stdout.write(
                render_properties(records, lock_evidence, metadata_evidence)
            )
        return 0
    except InventoryError as error:
        parser.exit(1, f"RUNTIME_LOCK_INVENTORY_CANDIDATE=REJECTED\nERROR={error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
