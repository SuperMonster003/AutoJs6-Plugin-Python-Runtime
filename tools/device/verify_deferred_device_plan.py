#!/usr/bin/env python3
"""Validate the deferred device plan without invoking Gradle, ADB, or a device."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable


SCHEMA = "autojs6-python-runtime-deferred-device-plan-v1"
PROTECTED_SERIAL = "QV710AF65F"
SERIAL_PLACEHOLDER = "${serial}"
ADB_PREFIX = ["adb", "-s", SERIAL_PLACEHOLDER]
MAX_PLAN_BYTES = 64 * 1024

TOP_LEVEL_KEYS = {
    "schema",
    "status",
    "executionAuthorized",
    "scope",
    "protectedSerials",
    "soakCompletionGate",
    "targetSelection",
    "toolPolicy",
    "futureAdbArgvTemplates",
    "forbiddenOperations",
    "evidencePolicy",
}
EXPECTED_TEMPLATE_IDS = {
    "preflight-state",
    "preflight-api",
    "preflight-abi",
    "instrumentation",
    "restore-verification",
}
REQUIRED_FORBIDDEN_OPERATIONS = {
    "gradle",
    "gradlew",
    "gradlew.bat",
    "connectedAndroidTest",
    "connectedCheck",
    "adb-without-exact-serial",
}
FORBIDDEN_ACCEPTANCE_CLAIMS = {"PASS", "PASSED", "READY", "COMPLETED"}


class PlanValidationError(ValueError):
    pass


def _reject_duplicate_keys(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise PlanValidationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_plan(path: Path) -> dict[str, Any]:
    resolved = path.resolve(strict=True)
    if path.is_symlink() or not resolved.is_file():
        raise PlanValidationError("plan must be a regular non-symlink file")
    if resolved.stat().st_size > MAX_PLAN_BYTES:
        raise PlanValidationError(f"plan exceeds {MAX_PLAN_BYTES} bytes")
    try:
        text = resolved.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise PlanValidationError("plan must be strict UTF-8") from error
    try:
        value = json.loads(text, object_pairs_hook=_reject_duplicate_keys)
    except json.JSONDecodeError as error:
        raise PlanValidationError(f"invalid JSON: {error.msg}") from error
    if not isinstance(value, dict):
        raise PlanValidationError("plan root must be an object")
    return value


def _require_exact_keys(value: Any, expected: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PlanValidationError(f"{label} must be an object")
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise PlanValidationError(f"{label} key mismatch; missing={missing}, extra={extra}")
    return value


def _require_false(value: Any, label: str) -> None:
    if value is not False:
        raise PlanValidationError(f"{label} must be false while the plan is deferred")


def _validate_scope(plan: dict[str, Any]) -> None:
    scope = _require_exact_keys(
        plan["scope"],
        {"repository", "stage", "planOnly"},
        "scope",
    )
    if scope["repository"] != "AutoJs6-Plugin-Python-Runtime":
        raise PlanValidationError("scope.repository drifted")
    if scope["stage"] != "R2":
        raise PlanValidationError("scope.stage must be R2")
    if scope["planOnly"] is not True:
        raise PlanValidationError("scope.planOnly must be true")


def _validate_protected_serials(plan: dict[str, Any]) -> None:
    serials = plan["protectedSerials"]
    if not isinstance(serials, list) or not serials:
        raise PlanValidationError("protectedSerials must be a non-empty array")
    if any(not isinstance(item, str) or not item.strip() for item in serials):
        raise PlanValidationError("protectedSerials must contain non-empty strings")
    if len(serials) != len(set(serials)):
        raise PlanValidationError("protectedSerials must be unique")
    if PROTECTED_SERIAL not in serials:
        raise PlanValidationError(f"{PROTECTED_SERIAL} must remain protected")


def _validate_soak_gate(plan: dict[str, Any]) -> None:
    gate = _require_exact_keys(
        plan["soakCompletionGate"],
        {"required", "confirmed", "confirmationMustBeExplicit", "confirmationEvidence"},
        "soakCompletionGate",
    )
    if gate["required"] is not True:
        raise PlanValidationError("soak completion must remain required")
    _require_false(gate["confirmed"], "soakCompletionGate.confirmed")
    if gate["confirmationMustBeExplicit"] is not True:
        raise PlanValidationError("soak completion confirmation must be explicit")
    if gate["confirmationEvidence"] is not None:
        raise PlanValidationError("deferred plan cannot carry soak-completion evidence")


def _validate_target_selection(plan: dict[str, Any]) -> None:
    target = _require_exact_keys(
        plan["targetSelection"],
        {
            "serial",
            "exactSerialRequired",
            "environmentFallbackAllowed",
            "autoDiscoveryAllowed",
            "fallbackAllowed",
        },
        "targetSelection",
    )
    if target["serial"] is not None:
        raise PlanValidationError("deferred plan must not select a device serial")
    if target["exactSerialRequired"] is not True:
        raise PlanValidationError("future execution must require an exact explicit serial")
    for key in ("environmentFallbackAllowed", "autoDiscoveryAllowed", "fallbackAllowed"):
        _require_false(target[key], f"targetSelection.{key}")


def _contains_gradle_or_connected_token(argv: list[Any]) -> bool:
    for token in argv:
        if not isinstance(token, str):
            continue
        lowered = token.lower()
        if "gradle" in lowered or lowered.startswith("connected"):
            return True
    return False


def _validate_tool_policy(plan: dict[str, Any]) -> None:
    policy = _require_exact_keys(
        plan["toolPolicy"],
        {
            "gradleAllowed",
            "connectedTaskAllowed",
            "adbExecutionAllowedNow",
            "futureAdbRequiredPrefix",
        },
        "toolPolicy",
    )
    for key in ("gradleAllowed", "connectedTaskAllowed", "adbExecutionAllowedNow"):
        _require_false(policy[key], f"toolPolicy.{key}")
    if policy["futureAdbRequiredPrefix"] != ADB_PREFIX:
        raise PlanValidationError("future ADB prefix must be exactly adb -s ${serial}")

    templates = plan["futureAdbArgvTemplates"]
    if not isinstance(templates, list) or not templates:
        raise PlanValidationError("futureAdbArgvTemplates must be a non-empty array")
    ids: list[str] = []
    for index, raw_template in enumerate(templates):
        template = _require_exact_keys(raw_template, {"id", "argv"}, f"template[{index}]")
        template_id = template["id"]
        argv = template["argv"]
        if not isinstance(template_id, str) or not template_id:
            raise PlanValidationError(f"template[{index}].id must be a non-empty string")
        if not isinstance(argv, list) or any(not isinstance(item, str) or not item for item in argv):
            raise PlanValidationError(f"template[{index}].argv must be non-empty string arguments")
        if argv[: len(ADB_PREFIX)] != ADB_PREFIX:
            raise PlanValidationError(f"template {template_id} does not use exact adb -s ${'{'}serial{'}'} prefix")
        if argv.count("-s") != 1 or argv.count(SERIAL_PLACEHOLDER) != 1:
            raise PlanValidationError(f"template {template_id} must bind exactly one serial")
        if _contains_gradle_or_connected_token(argv):
            raise PlanValidationError(f"template {template_id} contains Gradle or a connected task")
        ids.append(template_id)
    if len(ids) != len(set(ids)):
        raise PlanValidationError("future ADB template ids must be unique")
    if set(ids) != EXPECTED_TEMPLATE_IDS:
        raise PlanValidationError("future ADB template set drifted")

    forbidden = plan["forbiddenOperations"]
    if not isinstance(forbidden, list) or any(not isinstance(item, str) for item in forbidden):
        raise PlanValidationError("forbiddenOperations must be a string array")
    if set(forbidden) != REQUIRED_FORBIDDEN_OPERATIONS or len(forbidden) != len(set(forbidden)):
        raise PlanValidationError("forbiddenOperations must contain the exact V1 deny set")


def _validate_evidence_policy(plan: dict[str, Any]) -> None:
    policy = _require_exact_keys(
        plan["evidencePolicy"],
        {"emitReceiptNow", "allowPassClaimNow", "currentClaim"},
        "evidencePolicy",
    )
    _require_false(policy["emitReceiptNow"], "evidencePolicy.emitReceiptNow")
    _require_false(policy["allowPassClaimNow"], "evidencePolicy.allowPassClaimNow")
    if policy["currentClaim"] != "NOT_RUN":
        raise PlanValidationError("deferred plan currentClaim must be NOT_RUN")
    if str(policy["currentClaim"]).upper() in FORBIDDEN_ACCEPTANCE_CLAIMS:
        raise PlanValidationError("deferred plan cannot contain an acceptance claim")


def validate_plan(plan: dict[str, Any]) -> None:
    _require_exact_keys(plan, TOP_LEVEL_KEYS, "plan")
    if plan["schema"] != SCHEMA:
        raise PlanValidationError(f"schema must be {SCHEMA}")
    if plan["status"] != "DEFERRED":
        raise PlanValidationError("status must remain DEFERRED")
    _require_false(plan["executionAuthorized"], "executionAuthorized")
    _validate_scope(plan)
    _validate_protected_serials(plan)
    _validate_soak_gate(plan)
    _validate_target_selection(plan)
    _validate_tool_policy(plan)
    _validate_evidence_policy(plan)


def default_plan_path() -> Path:
    return Path(__file__).with_name("deferred-device-plan-v1.json")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate the deferred plan without running Gradle, ADB, or a device.",
    )
    parser.add_argument("--plan", type=Path, default=default_plan_path())
    args = parser.parse_args(argv)
    try:
        validate_plan(load_plan(args.plan))
    except (OSError, PlanValidationError) as error:
        parser.exit(1, f"DEFERRED_DEVICE_PLAN=INVALID\nERROR={error}\n")
    print("DEFERRED_DEVICE_PLAN=VALID")
    print("EXECUTION_AUTHORIZED=NO")
    print("SOAK_COMPLETION_CONFIRMED=NO")
    print(f"PROTECTED_SERIAL={PROTECTED_SERIAL}")
    print("ACCEPTANCE_CLAIM=NOT_RUN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
