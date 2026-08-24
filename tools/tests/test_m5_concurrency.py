from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
GUIDE = ROOT / "docs" / "python" / "CONCURRENT_EXECUTION.md"
SEMANTICS = ROOT / "docs" / "python" / "PYTHON_SEMANTICS_CONTRACT.md"
LONG_RUNNING = ROOT / "docs" / "python" / "LONG_RUNNING_EXECUTION.md"
EXAMPLE = ROOT / "examples" / "python" / "m5_concurrency"
ROADMAP = ROOT / "ROADMAP.md"


class M5ConcurrencyTest(unittest.TestCase):
    def test_bounded_fifo_examples_compile_and_have_observable_order_markers(self) -> None:
        self.assertEqual(
            {"README.md", "first.py", "second.py"},
            {path.name for path in EXAMPLE.iterdir()},
        )
        first = (EXAMPLE / "first.py").read_text(encoding="utf-8")
        second = (EXAMPLE / "second.py").read_text(encoding="utf-8")
        compile(first, str(EXAMPLE / "first.py"), "exec")
        compile(second, str(EXAMPLE / "second.py"), "exec")
        for marker in ("first admitted", "first tick=", "first finished", "flush=True"):
            self.assertIn(marker, first)
        for marker in ("second admitted", "second finished", "flush=True"):
            self.assertIn(marker, second)
        self.assertIn("time.sleep(1)", first)
        self.assertNotIn("time.sleep", second)

    def test_contract_fixes_single_provider_and_host_queue_boundaries(self) -> None:
        guide = " ".join(GUIDE.read_text(encoding="utf-8").split())
        semantics = " ".join(SEMANTICS.read_text(encoding="utf-8").split())
        long_running = " ".join(LONG_RUNNING.read_text(encoding="utf-8").split())
        roadmap = " ".join(ROADMAP.read_text(encoding="utf-8").split())
        for marker in (
            "one active session",
            "32 more executions",
            "FIFO",
            "before source/workspace snapshot creation",
            "three-second handoff",
            "NESTED_PYTHON_NOT_ALLOWED",
            "not simultaneous CPython execution",
            "BUSY/SESSION_OPEN",
            "afca7b14c",
            "Android FIFO retest remains pending",
        ):
            self.assertIn(marker, guide)
        for marker in ("32 pending", "FIFO", "process-generation handoff"):
            self.assertIn(marker, semantics)
        self.assertIn("Host FIFO queue", long_running)
        self.assertIn("并发准入", roadmap)
        self.assertIn("并发首次尝试未形成 FIFO 验收", roadmap)


if __name__ == "__main__":
    unittest.main()
