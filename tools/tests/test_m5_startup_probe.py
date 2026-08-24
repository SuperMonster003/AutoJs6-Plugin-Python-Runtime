from __future__ import annotations

import json
import pathlib
import statistics
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "python" / "m5_startup_probe"
GUIDE = ROOT / "docs" / "python" / "PROCESS_PREWARM_EVALUATION.md"
ROADMAP = ROOT / "ROADMAP.md"


class M5StartupProbeTest(unittest.TestCase):
    def test_probe_project_is_bounded_and_compiles(self) -> None:
        self.assertEqual(
            {"README.md", "main.py", "project.json"},
            {path.name for path in EXAMPLE.iterdir()},
        )
        self.assertEqual(
            {"type": "python", "main": "main.py"},
            json.loads((EXAMPLE / "project.json").read_text(encoding="utf-8")),
        )
        source = (EXAMPLE / "main.py").read_text(encoding="utf-8")
        compile(source, str(EXAMPLE / "main.py"), "exec")
        for marker in (
            "time.time_ns() // 1_000_000",
            'engine["startedAtMillis"]',
            "startup_probe_ms=",
            "plugin_pid=",
            '"autojs6-python-startup-probe-v1"',
            "result.set(",
            "flush=True",
        ):
            self.assertIn(marker, source)
        self.assertNotIn("time.sleep", source)

    def test_probe_captures_timestamp_before_broker_import_and_call(self) -> None:
        source = (EXAMPLE / "main.py").read_text(encoding="utf-8")
        capture = source.index("first_python_wall_millis =")
        broker_import = source.index("from autojs6 import engines, result")
        broker_call = source.index("engine = engines.current()")
        self.assertLess(capture, broker_import)
        self.assertLess(capture, broker_call)
        self.assertIn("first_python_wall_millis < engine_started_at_millis", source)

    def test_accepted_samples_close_retention_evaluation(self) -> None:
        samples = [441, 447, 429, 427, 428]
        plugin_pids = [26868, 27018, 27055, 27091, 27121]
        self.assertEqual(429, statistics.median(samples))
        self.assertEqual(428.5, statistics.median(samples[1:]))
        self.assertEqual(427, min(samples))
        self.assertEqual(447, max(samples))
        self.assertEqual(20, max(samples) - min(samples))
        self.assertEqual(5, len(set(plugin_pids)))
        self.assertTrue(all(sample <= 1000 for sample in samples))

    def test_guide_and_roadmap_close_measurement_without_retention(self) -> None:
        guide = " ".join(GUIDE.read_text(encoding="utf-8").split())
        roadmap = " ".join(ROADMAP.read_text(encoding="utf-8").split())
        for marker in (
            "launch-to-first-Python latency",
            "Run the project five times",
            "median above 1000 ms",
            "retain per-execution retirement",
            "441 ms",
            "428.5 ms",
            "five Plugin PIDs are distinct",
            "NO PROCESS RETENTION",
            "does not by itself claim a complete device matrix",
        ):
            self.assertIn(marker, guide)
        for marker in (
            "[x] [P] **进程预热评估**",
            "441/447/429/427/428 ms",
            "429 ms",
            "428.5 ms",
            "NO PROCESS RETENTION",
            "M5 核心交付收口",
        ):
            self.assertIn(marker, roadmap)


if __name__ == "__main__":
    unittest.main()
