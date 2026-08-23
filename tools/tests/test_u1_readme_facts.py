from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
README_DIR = ROOT / ".readme"
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


class U1ReadmeFactsTest(unittest.TestCase):
    def test_all_language_sources_describe_protocol_15_broker_and_existing_boundaries(self) -> None:
        common = json.loads((README_DIR / "common.json").read_text(encoding="utf-8"))
        self.assertEqual("0.3.0-alpha.2", common["release_target"])
        self.assertIn("protocol 1.5", common["release_state"])
        self.assertIn("complete first low-risk", common["release_state"])
        self.assertEqual("1 MiB", common["max_stdin_bytes"])
        self.assertEqual("1.0-1.5", common["protocol_version"])
        self.assertEqual("64 KiB", common["max_structured_json_bytes"])
        self.assertEqual("16", common["max_output_artifacts"])
        self.assertEqual("16 MiB", common["max_output_bytes"])
        self.assertEqual("16384", common["max_output_chunks"])
        self.assertEqual("30 min", common["max_timeout"])
        self.assertEqual("1024", common["max_host_capability_calls"])
        self.assertEqual("64 KiB", common["max_host_capability_message_bytes"])
        self.assertEqual("32 KiB", common["max_host_capability_text_bytes"])
        self.assertEqual("5 s", common["host_capability_call_timeout"])
        for code in LANGUAGE_CODES:
            with self.subTest(code=code):
                source = json.loads(
                    (README_DIR / f"lang_{code}.json").read_text(encoding="utf-8")
                )
                self.assertIn("{{ max_stdin_bytes }}", source["features"][1])
                self.assertIn("1.3", source["features"][1])
                self.assertIn("`getpass.getpass()`", source["features"][1])
                result_features = [item for item in source["features"] if "1.4" in item]
                self.assertEqual(1, len(result_features))
                self.assertIn("{{ max_structured_json_bytes }}", result_features[0])
                self.assertIn("{{ max_output_artifacts }}", result_features[0])
                self.assertIn("stdout", result_features[0])
                broker_features = [item for item in source["features"] if "1.5" in item]
                self.assertEqual(1, len(broker_features))
                self.assertIn("`toast`", broker_features[0])
                self.assertIn("`clip.get/set`", broker_features[0])
                self.assertIn("`app.launch/launch_app/open_url`", broker_features[0])
                self.assertIn("`device.info`", broker_features[0])
                self.assertIn("`console.log/warn/error`", broker_features[0])
                self.assertIn("`notice`", broker_features[0])
                self.assertIn("{{ max_stdin_bytes }}", source["p_plugin_scope"])
                self.assertIn("1.3", source["p_plugin_scope"])
                self.assertIn("1.4", source["p_plugin_scope"])
                self.assertIn("1.5", source["p_plugin_scope"])
                self.assertIn("SHA-256", source["p_plugin_scope"])
                self.assertIn("stdout", source["p_plugin_scope"])
                self.assertIn("`sys.stdin`", source["p_plugin_scope"])
                self.assertIn("`getpass.getpass()`", source["p_plugin_scope"])
                result_limits = [item for item in source["security_limits"] if "SHA-256" in item]
                self.assertEqual(1, len(result_limits))
                for placeholder in (
                    "{{ max_structured_json_bytes }}",
                    "{{ max_output_artifacts }}",
                    "{{ max_output_artifact_path_bytes }}",
                    "{{ max_output_artifact_bytes }}",
                    "{{ max_total_output_artifact_bytes }}",
                ):
                    self.assertIn(placeholder, result_limits[0])
                broker_limits = [item for item in source["security_limits"] if "1.5" in item]
                self.assertEqual(1, len(broker_limits))
                for placeholder in (
                    "{{ max_host_capability_calls }}",
                    "{{ max_host_capability_message_bytes }}",
                    "{{ max_host_capability_text_bytes }}",
                    "{{ host_capability_call_timeout }}",
                ):
                    self.assertIn(placeholder, broker_limits[0])
                network_limits = [item for item in source["security_limits"] if "INTERNET" in item]
                self.assertEqual(1, len(network_limits))
                self.assertIn("pip", network_limits[0])
                self.assertIn("{{ max_stdin_bytes }}", source["unsupported_capabilities"][0])
                self.assertIn("`sys.stdin`", source["unsupported_capabilities"][0])
                self.assertIn("`getpass.getpass()`", source["unsupported_capabilities"][0])
                self.assertTrue(
                    any("OCR" in item for item in source["unsupported_capabilities"]),
                    f"{code} does not bound the remaining broker surface",
                )
                self.assertIn("16 KB", source["p_build_architecture"])
                self.assertIn("gate", source["p_build_architecture"].lower())

    def test_all_changelog_sources_record_protocol_13_and_14_scoped_features(self) -> None:
        changelog_dir = ROOT / ".changelog"
        for code in LANGUAGE_CODES:
            with self.subTest(code=code):
                source = json.loads(
                    (changelog_dir / f"lang_{code}.json").read_text(encoding="utf-8")
                )
                complete_slice = source["$data"]["v0.3.0-alpha.2"]
                self.assertEqual("2026/08/23", complete_slice["released_date"])
                public_api = complete_slice["feature"]
                self.assertEqual(1, len(public_api))
                self.assertIn("`autojs6.device.info()`", public_api[0])
                self.assertIn("`autojs6.console.log/warn/error`", public_api[0])
                self.assertIn("`autojs6.notice`", public_api[0])
                self.assertIn("`PERMISSION_DENIED`", complete_slice["improvement"][0])

                broker = source["$data"]["v0.3.0-alpha.1"]
                self.assertEqual("2026/08/23", broker["released_date"])
                protocol_15 = [item for item in broker["feature"] if "1.5" in item]
                self.assertEqual(1, len(protocol_15))
                self.assertIn("1024", protocol_15[0])
                self.assertIn("64 KiB", protocol_15[0])
                public_api = [item for item in broker["feature"] if "`autojs6.toast`" in item]
                self.assertEqual(1, len(public_api))
                self.assertIn("`autojs6.clip.get/set`", public_api[0])
                self.assertIn("`autojs6.app.launch/launch_app/open_url`", public_api[0])
                current = source["$data"]["v0.2.0-alpha.1"]
                self.assertIn("E2", current["hint"][0])
                self.assertIn("R2 E3", current["hint"][0])
                protocol_13 = [item for item in current["feature"] if "1.3" in item]
                protocol_14 = [item for item in current["feature"] if "1.4" in item]
                self.assertEqual(1, len(protocol_13))
                self.assertEqual(1, len(protocol_14))
                self.assertIn("`input()`", protocol_13[0])
                self.assertIn("`getpass.getpass()`", protocol_13[0])
                self.assertIn("`sys.stdin`", protocol_13[0])
                self.assertIn("SHA-256", protocol_14[0])
                self.assertIn("stdout", protocol_14[0])
                network_changes = [item for item in current["improvement"] if "INTERNET" in item]
                limit_changes = [item for item in current["improvement"] if "16 MiB" in item]
                self.assertEqual(1, len(network_changes))
                self.assertEqual(1, len(limit_changes))
                self.assertIn("pip", network_changes[0])
                self.assertIn("16384", limit_changes[0])

    def test_generated_readmes_contain_no_unresolved_or_stale_stdin_claim(self) -> None:
        stale_fragments = (
            "stdin snapshots remain disabled",
            "stdin snapshot 仍关闭",
            "stdin snapshot 仍關閉",
            "stdin snapshot reste désactivé",
            "stdin snapshot sigue desactivado",
            "stdin snapshot は無効",
            "stdin snapshot은 비활성",
            "stdin snapshot остается выключенным",
            "يظل stdin snapshot معطلا",
        )
        for code in LANGUAGE_CODES:
            with self.subTest(code=code):
                body = (README_DIR / f"README-{code}.md").read_text(encoding="utf-8")
                self.assertIn("1 MiB", body)
                self.assertIn("1.0-1.5", body)
                self.assertIn("64 KiB", body)
                self.assertIn("16 MiB", body)
                self.assertIn("16384", body)
                self.assertIn("30 min", body)
                self.assertIn("INTERNET", body)
                self.assertIn("SHA-256", body)
                self.assertIn("autojs6.toast", body)
                self.assertNotIn("{{", body)
                lowered = body.lower()
                for stale in stale_fragments:
                    self.assertNotIn(stale.lower(), lowered)

    def test_primary_generated_readmes_state_scoped_foreground_input_and_no_page_gate(self) -> None:
        simplified = (ROOT / "README.md").read_text(encoding="utf-8")
        english = (README_DIR / "README-en.md").read_text(encoding="utf-8")
        self.assertEqual(
            simplified,
            (README_DIR / "README-zh-Hans.md").read_text(encoding="utf-8"),
        )
        self.assertIn("协议 1.3 在快照 EOF 后为内置 `input()`", simplified)
        self.assertIn("`getpass.getpass()` 使用隐藏回显", simplified)
        self.assertIn("后台启动绝不打开输入 UI", simplified)
        self.assertIn("直接 `sys.stdin` 始终有限", simplified)
        self.assertIn("协议 1.4 增加显式严格 JSON 结果", simplified)
        self.assertIn("协议 1.5 增加绑定单次执行", simplified)
        self.assertIn("`autojs6.toast`", simplified)
        self.assertIn("绝不被解析为结果", simplified)
        self.assertIn("API 37 x86_64 16 KB page 模拟器的聚焦冒烟", simplified)
        self.assertIn("不等同于完整兼容性 gate", simplified)
        self.assertIn("Protocol 1.3 adds Host-owned, foreground-only prompt/reply", english)
        self.assertIn("`getpass.getpass()` uses hidden echo", english)
        self.assertIn("background launches never open input UI", english)
        self.assertIn("Direct `sys.stdin` remains finite", english)
        self.assertIn("Protocol 1.4 adds explicit strict JSON", english)
        self.assertIn("Protocol 1.5 adds a pure-data Host capability broker", english)
        self.assertIn("`autojs6.toast`", english)
        self.assertIn("never parsed as a result", english)
        self.assertIn("API 37 x86_64 16 KB-page emulator smoke has passed", english)
        self.assertIn("not a comprehensive compatibility gate", english)


if __name__ == "__main__":
    unittest.main()
