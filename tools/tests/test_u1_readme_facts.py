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
    def test_all_language_sources_describe_bounded_snapshot_and_page_gate_boundary(self) -> None:
        common = json.loads((README_DIR / "common.json").read_text(encoding="utf-8"))
        self.assertEqual("1 MiB", common["max_stdin_bytes"])
        for code in LANGUAGE_CODES:
            with self.subTest(code=code):
                source = json.loads(
                    (README_DIR / f"lang_{code}.json").read_text(encoding="utf-8")
                )
                self.assertIn("{{ max_stdin_bytes }}", source["features"][1])
                self.assertIn("{{ max_stdin_bytes }}", source["p_plugin_scope"])
                self.assertIn("{{ max_stdin_bytes }}", source["unsupported_capabilities"][0])
                self.assertIn("16 KB", source["p_build_architecture"])
                self.assertIn("gate", source["p_build_architecture"].lower())

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
                self.assertNotIn("{{", body)
                lowered = body.lower()
                for stale in stale_fragments:
                    self.assertNotIn(stale.lower(), lowered)

    def test_primary_generated_readmes_state_no_live_input_and_no_page_gate(self) -> None:
        simplified = (ROOT / "README.md").read_text(encoding="utf-8")
        english = (README_DIR / "README-en.md").read_text(encoding="utf-8")
        self.assertEqual(
            simplified,
            (README_DIR / "README-zh-Hans.md").read_text(encoding="utf-8"),
        )
        self.assertIn("不提供实时交互式 stdin", simplified)
        self.assertIn("16 KB page 兼容性当前没有专用 gate", simplified)
        self.assertIn("Live interactive stdin is unavailable", english)
        self.assertIn("16 KB page compatibility currently has no dedicated gate", english)


if __name__ == "__main__":
    unittest.main()
