#!/usr/bin/env python3
"""Read-only M6 current-tree candidate checks.

This is deliberately smaller than the historical v0.1.0 evidence verifiers.
It does not use a device, signing material, network access, tags, or publication.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from types import ModuleType


ROOT = Path(__file__).resolve().parents[1]
LANGUAGE_CODES = (
    "zh-Hans",
    "zh-Hant-HK",
    "zh-Hant-TW",
    "en",
    "fr",
    "es",
    "ja",
    "ko",
    "ru",
    "ar",
)
SEMVER_PATTERN = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-(?:0|[1-9A-Za-z][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9A-Za-z][0-9A-Za-z-]*))*)?$"
)
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class CandidateError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CandidateError(message)


def read_unique_properties(path: Path) -> dict[str, str]:
    require(path.is_file(), f"missing properties file: {path}")
    result: dict[str, str] = {}
    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line or line.startswith(("#", "!")):
            continue
        require("=" in line, f"malformed property at {path}:{line_number}")
        key, value = (part.strip() for part in line.split("=", 1))
        require(bool(key), f"empty property name at {path}:{line_number}")
        require(key not in result, f"duplicate property {key!r} in {path}")
        result[key] = value
    return result


def validate_version_name(version_name: str) -> None:
    require(
        SEMVER_PATTERN.fullmatch(version_name) is not None,
        f"VERSION_NAME is not supported SemVer: {version_name!r}",
    )


def git_output(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    require(
        completed.returncode == 0,
        f"git {' '.join(arguments)} failed: {completed.stderr.strip()}",
    )
    return completed.stdout.strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_generator(root: Path) -> ModuleType:
    path = root / ".python" / "generate_markdown.py"
    require(path.is_file(), f"missing Markdown generator: {path}")
    spec = importlib.util.spec_from_file_location("m6_generate_markdown", path)
    require(spec is not None and spec.loader is not None, "cannot load Markdown generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_changelog_sources(root: Path, version_name: str) -> int:
    expected_version = f"v{version_name}"
    expected_order: list[str] | None = None
    allowed_fields = {
        "released_date",
        "hint",
        "feature",
        "fix",
        "improvement",
        "dependency",
    }
    for code in LANGUAGE_CODES:
        path = root / ".changelog" / f"lang_{code}.json"
        require(path.is_file(), f"missing changelog locale: {code}")
        document = json.loads(path.read_text(encoding="utf-8"))
        data = document.get("$data")
        require(isinstance(data, dict) and data, f"empty changelog data: {code}")
        order = list(data)
        require(order[0] == expected_version, f"current changelog is not first for {code}")
        if expected_order is None:
            expected_order = order
        else:
            require(order == expected_order, f"changelog order differs for {code}")
        entry = data[expected_version]
        require(isinstance(entry, dict), f"current changelog entry is invalid for {code}")
        require(set(entry) <= allowed_fields, f"unknown current changelog field for {code}")
        require(
            re.fullmatch(r"\d{4}/\d{2}/\d{2}", str(entry.get("released_date", "")))
            is not None,
            f"current changelog date is invalid for {code}",
        )
        for field in ("hint", "feature", "fix", "improvement", "dependency"):
            values = entry.get(field, [])
            require(isinstance(values, list), f"{field} must be a list for {code}")
            require(
                all(isinstance(value, str) and value.strip() for value in values),
                f"{field} contains an empty item for {code}",
            )
        require(entry.get("hint"), f"current changelog hint is missing for {code}")
        require(
            any(entry.get(field) for field in ("feature", "fix", "improvement", "dependency")),
            f"current changelog has no change item for {code}",
        )
    return len(LANGUAGE_CODES)


def expected_generated_documents(root: Path) -> dict[Path, str]:
    generator = load_generator(root)
    languages, changelogs = generator.load_languages()
    expected: dict[Path, str] = {}
    readme_template = (root / ".readme" / "template_readme.md").read_text(
        encoding="utf-8"
    )
    for code in LANGUAGE_CODES:
        output = generator.render_template(
            readme_template,
            generator.build_readme_values(code, languages, changelogs),
        )
        require(generator.TEMPLATE_PATTERN.search(output) is None, f"README placeholder: {code}")
        expected[root / ".readme" / f"README-{code}.md"] = output
        if code == generator.LANGUAGE_CODE_DEFAULT:
            expected[root / "README.md"] = output

    changelog_template = (root / ".changelog" / "template_changelog.md").read_text(
        encoding="utf-8"
    )
    for code in LANGUAGE_CODES:
        values = dict(languages[code])
        values["placeholder_release_history"] = generator.format_changelog_items(
            changelogs[code]
        ).rstrip()
        output = generator.render_template(changelog_template, values)
        require(
            generator.TEMPLATE_PATTERN.search(output) is None,
            f"CHANGELOG placeholder: {code}",
        )
        for name in generator.ANDROID_CHANGELOG_ALIASES.get(code, [code]):
            expected[
                root / "app" / "src" / "main" / "assets" / "doc" / f"CHANGELOG-{name}.md"
            ] = output
        if code == generator.LANGUAGE_CODE_DEFAULT:
            expected[root / "app" / "src" / "main" / "assets" / "doc" / "CHANGELOG.md"] = output
    return expected


def validate_generated_documents(root: Path) -> int:
    expected = expected_generated_documents(root)
    stale = [
        path.relative_to(root).as_posix()
        for path, content in expected.items()
        if not path.is_file() or path.read_text(encoding="utf-8") != content
    ]
    require(not stale, f"generated Markdown is stale: {', '.join(stale[:5])}")
    return len(expected)


def validate_host_api_aars(root: Path) -> tuple[int, str]:
    lock_path = root / "locks" / "host-api-aars.lock"
    lock = read_unique_properties(lock_path)
    prefixes = ("common-plugin-api", "protocol-wire-api", "python-runtime-api")
    expected_keys = {"format"} | {
        f"{prefix}.{suffix}" for prefix in prefixes for suffix in ("file", "sha256")
    }
    require(set(lock) == expected_keys, "Host API AAR lock keys are not exact")
    require(lock["format"] == "1", "Host API AAR lock format is not 1")
    files: set[str] = set()
    for prefix in prefixes:
        file_name = lock[f"{prefix}.file"]
        expected_hash = lock[f"{prefix}.sha256"]
        require(Path(file_name).name == file_name, f"nested Host AAR path: {file_name}")
        require(file_name.endswith(".aar"), f"Host API file is not an AAR: {file_name}")
        require(file_name not in files, f"duplicate Host API AAR: {file_name}")
        files.add(file_name)
        require(SHA256_PATTERN.fullmatch(expected_hash) is not None, f"invalid AAR hash: {prefix}")
        path = root / "libs" / file_name
        require(path.is_file(), f"missing locked Host API AAR: {file_name}")
        require(sha256(path) == expected_hash, f"Host API AAR hash mismatch: {file_name}")
    lock_text = lock_path.read_text(encoding="utf-8")
    host_match = re.search(r"(?m)^# Host HEAD: ([0-9a-f]{40,64}) \(clean source tree\)$", lock_text)
    require(host_match is not None, "Host API AAR lock lacks a clean source HEAD")
    return len(files), host_match.group(1)


def require_empty_release_directories(root: Path) -> None:
    for relative in ("release", "releases"):
        path = root / relative
        if path.exists():
            require(path.is_dir(), f"release output path is not a directory: {relative}")
            require(
                not any(item.is_file() for item in path.rglob("*")),
                f"stale release output exists in {relative}/",
            )


def inspect_source_candidate(root: Path = ROOT) -> dict[str, str | int]:
    version = read_unique_properties(root / "version.properties")
    version_name = version.get("VERSION_NAME", "")
    validate_version_name(version_name)
    try:
        version_build = int(version.get("VERSION_BUILD", ""))
    except ValueError as error:
        raise CandidateError("VERSION_BUILD is not an integer") from error
    require(version_build > 0, "VERSION_BUILD is not positive")

    common = json.loads((root / ".readme" / "common.json").read_text(encoding="utf-8"))
    release_target = common.get("release_target")
    require(release_target == version_name, "README release_target differs from VERSION_NAME")

    head = git_output(root, "rev-parse", "--verify", "HEAD")
    require(re.fullmatch(r"[0-9a-fA-F]{40,64}", head) is not None, "Git HEAD is invalid")
    try:
        commit_count = int(git_output(root, "rev-list", "--count", "HEAD"))
    except ValueError as error:
        raise CandidateError("Git commit count is not an integer") from error
    require(version_build == commit_count, "VERSION_BUILD differs from Git commit count")
    require(
        not git_output(root, "status", "--porcelain", "--untracked-files=all"),
        "Git worktree is not clean",
    )

    locale_count = validate_changelog_sources(root, version_name)
    generated_count = validate_generated_documents(root)
    aar_count, host_head = validate_host_api_aars(root)
    require_empty_release_directories(root)
    require(
        (root / "docs" / "maintenance" / "M6_RELEASE_PROCESS.md").is_file(),
        "M6 release process document is missing",
    )
    return {
        "version_name": version_name,
        "version_build": version_build,
        "head": head,
        "commit_count": commit_count,
        "locale_count": locale_count,
        "generated_count": generated_count,
        "aar_count": aar_count,
        "host_head": host_head,
    }


def print_source_summary(summary: dict[str, str | int]) -> None:
    print("M6_CANDIDATE_SOURCE=PASS")
    print(f"VERSION_NAME={summary['version_name']}")
    print(f"VERSION_BUILD={summary['version_build']}")
    print(f"GIT_HEAD={summary['head']}")
    print(f"GIT_COMMIT_COUNT={summary['commit_count']}")
    print(f"CHANGELOG_LOCALES={summary['locale_count']}")
    print(f"GENERATED_DOCUMENTS={summary['generated_count']}_IN_SYNC")
    print(f"HOST_API_AARS={summary['aar_count']}_SHA256_MATCH")
    print(f"HOST_API_SOURCE_HEAD={summary['host_head']}")
    print("NETWORK=NOT_USED")
    print("ADB=NOT_USED")
    print("SIGNING=NOT_USED")
    print("PUBLICATION=NOT_PERFORMED")


def run_step(label: str, command: list[str], env: dict[str, str]) -> None:
    print(f"M6_STEP={label}", flush=True)
    completed = subprocess.run(command, cwd=ROOT, env=env, check=False)
    require(completed.returncode == 0, f"{label} failed with exit code {completed.returncode}")


def checked_python313(command: list[str]) -> Path | None:
    completed = subprocess.run(
        [
            *command,
            "-c",
            "import pathlib,sys; print(pathlib.Path(sys.executable).resolve()); "
            "print(f'{sys.version_info.major}.{sys.version_info.minor}')",
        ],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode != 0:
        return None
    lines = completed.stdout.splitlines()
    if len(lines) != 2 or lines[1].strip() != "3.13":
        return None
    path = Path(lines[0].strip())
    return path if path.is_file() else None


def resolve_python313() -> Path:
    candidates: list[list[str]] = []
    configured = os.environ.get("AUTOJS6_PYTHON313")
    if configured:
        configured_path = Path(configured).expanduser()
        if configured_path.is_dir():
            configured_path /= "python.exe" if os.name == "nt" else "python3.13"
        candidates.append([str(configured_path)])
    candidates.append([sys.executable])
    discovered = shutil.which("python3.13")
    if discovered:
        candidates.append([discovered])
    if os.name == "nt":
        launcher = shutil.which("py.exe") or shutil.which("py")
        if launcher:
            candidates.append([launcher, "-3.13"])
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            candidates.append(
                [str(Path(local_app_data) / "Programs" / "Python" / "Python313" / "python.exe")]
            )
        candidates.append([r"C:\Program Files\Python313\python.exe"])
    for command in candidates:
        if len(command) == 1 and not Path(command[0]).is_file():
            continue
        resolved = checked_python313(command)
        if resolved is not None:
            return resolved
    raise CandidateError(
        "--full requires Python 3.13; set AUTOJS6_PYTHON313 to its executable or directory"
    )


def run_full_gate() -> None:
    python313 = resolve_python313()
    print(f"BUILD_PYTHON={python313}")
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PATH"] = str(python313.parent) + os.pathsep + env.get("PATH", "")
    run_step(
        "PORTABLE_TESTS",
        [
            str(python313),
            "-B",
            "-m",
            "unittest",
            "discover",
            "-s",
            "tools/tests",
            "-p",
            "test_*.py",
            "-v",
        ],
        env,
    )
    powershell = (
        shutil.which("pwsh.exe")
        or shutil.which("pwsh")
        or shutil.which("powershell.exe")
    )
    require(powershell is not None, "PowerShell is required for the R2 static gate")
    powershell_command = [powershell, "-NoProfile"]
    if os.name == "nt":
        powershell_command.extend(["-ExecutionPolicy", "Bypass"])
    powershell_command.extend(["-File", str(ROOT / "tools" / "verify-r2-static.ps1")])
    run_step("R2_STATIC", powershell_command, env)
    wrapper = ROOT / ("gradlew.bat" if os.name == "nt" else "gradlew")
    run_step(
        "OFFLINE_DEBUG_BUILD",
        [
            str(wrapper),
            "--offline",
            "--console=plain",
            ":app:testDebugUnitTest",
            ":app:assembleDebug",
        ],
        env,
    )
    require(
        not git_output(ROOT, "status", "--porcelain", "--untracked-files=all"),
        "full gate changed the tracked worktree",
    )
    print("M6_CANDIDATE_FULL=PASS")


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    profile = parser.add_mutually_exclusive_group(required=True)
    profile.add_argument("--source-only", action="store_true", help="run read-only source checks")
    profile.add_argument("--full", action="store_true", help="also run tests and offline debug build")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        summary = inspect_source_candidate()
        print_source_summary(summary)
        if args.full:
            run_full_gate()
    except (CandidateError, OSError, json.JSONDecodeError) as error:
        print("M6_CANDIDATE=FAIL", file=sys.stderr)
        print(f"BLOCKER={error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
