from __future__ import annotations

import pathlib
import os
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SOURCE = ROOT / "app" / "src" / "main" / "python"
sys.path.insert(0, str(PYTHON_SOURCE))

from autojs6_runtime.bootstrap import run_project, run_source  # noqa: E402


def run(source: bytes, *, maximum_bytes: int = 4096, maximum_chunk: int = 32, maximum_chunks: int = 128):
    return run_source(
        source,
        "main.py",
        ["first", "second"],
        maximum_bytes,
        maximum_chunk,
        maximum_chunks,
    )


class BootstrapTest(unittest.TestCase):
    def test_finite_output_keeps_shared_stream_order_and_chunks(self) -> None:
        outcome = run(
            b"import sys\n"
            b"sys.stdout.write('out')\n"
            b"sys.stderr.write('err')\n"
            b"sys.stdout.buffer.write(b'0123456789')\n",
            maximum_chunk=4,
        )
        self.assertEqual("completed", outcome["status"])
        self.assertEqual(0, outcome["exit_code"])
        self.assertEqual(
            [
                ("stdout", b"out"),
                ("stderr", b"err"),
                ("stdout", b"0123"),
                ("stdout", b"4567"),
                ("stdout", b"89"),
            ],
            list(outcome["output"]),
        )

    def test_system_exit_is_a_bounded_result(self) -> None:
        outcome = run(b"raise SystemExit(7)\n")
        self.assertEqual("completed", outcome["status"])
        self.assertEqual(7, outcome["exit_code"])

    def test_non_integer_system_exit_uses_stderr_and_exit_one(self) -> None:
        outcome = run(b"raise SystemExit('stop')\n")
        self.assertEqual("completed", outcome["status"])
        self.assertEqual(1, outcome["exit_code"])
        self.assertEqual(b"stop\n", b"".join(chunk for _, chunk in outcome["output"]))

    def test_syntax_error_is_structured(self) -> None:
        outcome = run(b"if True print('broken')\n")
        self.assertEqual("failed", outcome["status"])
        self.assertEqual("SyntaxError", outcome["exception_type"])
        self.assertTrue(any(frame["origin"] == "project" for frame in outcome["traceback"]))

    def test_runtime_exception_is_structured(self) -> None:
        outcome = run(b"raise ValueError('broken')\n")
        self.assertEqual("failed", outcome["status"])
        self.assertEqual("ValueError", outcome["exception_type"])
        self.assertEqual("broken", outcome["exception_message"])
        self.assertTrue(any(frame["file_name"] == "main.py" for frame in outcome["traceback"]))

    def test_output_byte_limit_fails_closed(self) -> None:
        outcome = run(b"print('0123456789')\n", maximum_bytes=5)
        self.assertEqual("output_limit", outcome["status"])
        self.assertLessEqual(sum(len(chunk) for _, chunk in outcome["output"]), 5)

    def test_output_chunk_count_limit_fails_closed(self) -> None:
        outcome = run(b"print('abcdef', end='')\n", maximum_chunk=1, maximum_chunks=3)
        self.assertEqual("output_limit", outcome["status"])
        self.assertEqual(3, len(outcome["output"]))

    def test_stdio_and_argv_are_restored(self) -> None:
        stdout, stderr, argv = sys.stdout, sys.stderr, sys.argv
        run(b"print(__name__, __file__, *sys.argv)\n")
        self.assertIs(stdout, sys.stdout)
        self.assertIs(stderr, sys.stderr)
        self.assertIs(argv, sys.argv)

    def test_project_uses_private_root_for_imports_and_relative_files_then_restores_process_state(self) -> None:
        previous_cwd, previous_path = os.getcwd(), list(sys.path)
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            source = (
                b"import helper\n"
                b"from pathlib import Path\n"
                b"print(helper.VALUE, Path('data.txt').read_text(encoding='utf-8'))\n"
            )
            (root / "main.py").write_bytes(source)
            (root / "helper.py").write_text("VALUE = 'imported'\n", encoding="utf-8")
            (root / "data.txt").write_text("relative", encoding="utf-8")

            outcome = run_project(source, "main.py", str(root), [], 4096, 64, 128)

        self.assertEqual("completed", outcome["status"])
        self.assertEqual(b"imported relative\n", b"".join(chunk for _, chunk in outcome["output"]))
        self.assertEqual(previous_cwd, os.getcwd())
        self.assertEqual(previous_path, sys.path)
        self.assertNotIn("helper", sys.modules)

    def test_project_traceback_uses_relative_project_names_without_private_root_leak(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            source = b"import pkg.broken\n"
            (root / "main.py").write_bytes(source)
            (root / "pkg").mkdir()
            (root / "pkg" / "__init__.py").write_text("", encoding="utf-8")
            (root / "pkg" / "broken.py").write_text("raise RuntimeError('project failure')\n", encoding="utf-8")

            outcome = run_project(source, "main.py", str(root), [], 4096, 64, 128)

        self.assertEqual("failed", outcome["status"])
        self.assertEqual("RuntimeError", outcome["exception_type"])
        project_names = [
            frame["file_name"] for frame in outcome["traceback"] if frame["origin"] == "project"
        ]
        self.assertIn("main.py", project_names)
        self.assertIn("pkg/broken.py", project_names)
        self.assertNotIn(str(root), repr(outcome["traceback"]))

    def test_nested_project_entry_imports_entry_sibling_before_workspace_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            source = b"import helper\nimport root_helper\nprint(helper.VALUE, root_helper.VALUE)\n"
            (root / "src").mkdir()
            (root / "src" / "main.py").write_bytes(source)
            (root / "src" / "helper.py").write_text("VALUE = 'sibling'\n", encoding="utf-8")
            (root / "root_helper.py").write_text("VALUE = 'root'\n", encoding="utf-8")

            outcome = run_project(source, "src/main.py", str(root), [], 4096, 64, 128)

        self.assertEqual("completed", outcome["status"])
        self.assertEqual(b"sibling root\n", b"".join(chunk for _, chunk in outcome["output"]))


if __name__ == "__main__":
    unittest.main()
