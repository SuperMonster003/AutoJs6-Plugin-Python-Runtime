from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from tools.device.verify_deferred_device_plan import (
    PlanValidationError,
    default_plan_path,
    load_plan,
    validate_plan,
)


class DeferredDevicePlanTest(unittest.TestCase):
    def canonical(self):
        return copy.deepcopy(load_plan(default_plan_path()))

    def assert_invalid(self, plan, message_fragment):
        with self.assertRaisesRegex(PlanValidationError, message_fragment):
            validate_plan(plan)

    def test_canonical_plan_is_deferred_and_valid(self):
        plan = self.canonical()
        validate_plan(plan)
        self.assertEqual("DEFERRED", plan["status"])
        self.assertFalse(plan["executionAuthorized"])
        self.assertEqual("NOT_RUN", plan["evidencePolicy"]["currentClaim"])

    def test_qv710af65f_must_remain_protected(self):
        plan = self.canonical()
        plan["protectedSerials"] = ["another-device"]
        self.assert_invalid(plan, "QV710AF65F must remain protected")

    def test_soak_cannot_be_marked_complete_in_deferred_v1(self):
        plan = self.canonical()
        plan["soakCompletionGate"]["confirmed"] = True
        self.assert_invalid(plan, "confirmed must be false")

    def test_deferred_plan_cannot_select_a_serial(self):
        plan = self.canonical()
        plan["targetSelection"]["serial"] = "emulator-5556"
        self.assert_invalid(plan, "must not select a device serial")

    def test_environment_or_auto_discovery_fallback_is_rejected(self):
        for key in ("environmentFallbackAllowed", "autoDiscoveryAllowed", "fallbackAllowed"):
            with self.subTest(key=key):
                plan = self.canonical()
                plan["targetSelection"][key] = True
                self.assert_invalid(plan, key)

    def test_every_future_adb_argv_requires_exact_serial_prefix(self):
        plan = self.canonical()
        plan["futureAdbArgvTemplates"][0]["argv"] = ["adb", "get-state"]
        self.assert_invalid(plan, r"exact adb -s \$\{serial\} prefix")

    def test_gradle_and_connected_tasks_are_rejected_from_templates(self):
        for token in ("gradlew.bat", "connectedDebugAndroidTest"):
            with self.subTest(token=token):
                plan = self.canonical()
                plan["futureAdbArgvTemplates"][0]["argv"].append(token)
                self.assert_invalid(plan, "Gradle or a connected task")

    def test_execution_authorization_is_rejected(self):
        plan = self.canonical()
        plan["executionAuthorized"] = True
        self.assert_invalid(plan, "executionAuthorized must be false")

    def test_receipt_or_acceptance_claim_is_rejected(self):
        receipt = self.canonical()
        receipt["evidencePolicy"]["emitReceiptNow"] = True
        self.assert_invalid(receipt, "emitReceiptNow must be false")

        claimed = self.canonical()
        claimed["evidencePolicy"]["allowPassClaimNow"] = True
        self.assert_invalid(claimed, "allowPassClaimNow must be false")

        passed = self.canonical()
        passed["evidencePolicy"]["currentClaim"] = "PASS"
        self.assert_invalid(passed, "currentClaim must be NOT_RUN")

    def test_duplicate_json_keys_fail_closed(self):
        plan = self.canonical()
        text = json.dumps(plan).replace(
            '"schema": "autojs6-python-runtime-deferred-device-plan-v1"',
            '"schema": "autojs6-python-runtime-deferred-device-plan-v1", "schema": "duplicate"',
            1,
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.json"
            path.write_text(text, encoding="utf-8")
            with self.assertRaisesRegex(PlanValidationError, "duplicate JSON key"):
                load_plan(path)


if __name__ == "__main__":
    unittest.main()
