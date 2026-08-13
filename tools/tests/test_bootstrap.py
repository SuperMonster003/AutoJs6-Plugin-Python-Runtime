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


def run(
    source: bytes,
    *,
    stdin: bytes = b"",
    maximum_bytes: int = 4096,
    maximum_chunk: int = 32,
    maximum_chunks: int = 128,
):
    return run_source(
        source,
        "main.py",
        ["first", "second"],
        maximum_bytes,
        maximum_chunk,
        maximum_chunks,
        b"",
        stdin,
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

    def test_input_prompt_reads_one_utf8_line(self) -> None:
        outcome = run(
            "name = input('名字: ')\nprint(f'你好, {name}!')\n".encode("utf-8"),
            stdin="世界\n".encode("utf-8"),
        )
        self.assertEqual("completed", outcome["status"])
        self.assertEqual("名字: 你好, 世界!\n".encode("utf-8"), b"".join(chunk for _, chunk in outcome["output"]))

    def test_stdin_text_reads_multiple_lines_with_universal_newlines(self) -> None:
        outcome = run(
            b"import sys\nprint(repr(sys.stdin.readline()), repr(sys.stdin.readline()), repr(sys.stdin.read()))\n",
            stdin="甲\r\n乙\r尾".encode("utf-8"),
        )
        self.assertEqual("completed", outcome["status"])
        self.assertEqual(
            "'甲\\n' '乙\\n' '尾'\n".encode("utf-8"),
            b"".join(chunk for _, chunk in outcome["output"]),
        )

    def test_stdin_readlines_and_final_line_without_newline(self) -> None:
        outcome = run(
            b"import sys\nprint([line.rstrip('\\n') for line in sys.stdin.readlines()])\n",
            stdin="first\nsecond".encode("utf-8"),
        )
        self.assertEqual("completed", outcome["status"])
        self.assertEqual(
            b"['first', 'second']\n",
            b"".join(chunk for _, chunk in outcome["output"]),
        )

    def test_missing_stdin_is_deterministic_eof(self) -> None:
        outcome = run(b"input('prompt>')\n")
        self.assertEqual("failed", outcome["status"])
        self.assertEqual("EOFError", outcome["exception_type"])
        self.assertEqual(b"prompt>", b"".join(chunk for _, chunk in outcome["output"]))

    def test_stdin_buffer_exposes_exact_snapshot_bytes(self) -> None:
        outcome = run(
            b"import sys\nprint(sys.stdin.buffer.read())\n",
            stdin=b"raw\x00\xff\r\n",
        )
        self.assertEqual("completed", outcome["status"])
        self.assertEqual(b"b'raw\\x00\\xff\\r\\n'\n", b"".join(chunk for _, chunk in outcome["output"]))

    def test_invalid_utf8_stdin_fails_on_text_decode(self) -> None:
        outcome = run(b"import sys\nsys.stdin.read()\n", stdin=b"valid\xff")
        self.assertEqual("failed", outcome["status"])
        self.assertEqual("UnicodeDecodeError", outcome["exception_type"])

    def test_source_requires_strict_utf8_even_with_encoding_cookie(self) -> None:
        outcome = run(b"# coding: latin-1\nprint('caf\xe9')\n")
        self.assertEqual("failed", outcome["status"])
        self.assertEqual("UnicodeDecodeError", outcome["exception_type"])

        conflicting_cookie = run(b"# coding: latin-1\nprint('ascii')\n")
        self.assertEqual("failed", conflicting_cookie["status"])
        self.assertEqual("ValueError", conflicting_cookie["exception_type"])

        nul_source = run(b"print('before')\x00\n")
        self.assertEqual("failed", nul_source["status"])
        self.assertEqual("ValueError", nul_source["exception_type"])

    def test_stdlib_import_and_import_main_see_the_execution_module(self) -> None:
        outcome = run(
            b"import json\n"
            b"VALUE = 'execution-main'\n"
            b"import __main__\n"
            b"print(json.dumps({'value': __main__.VALUE}, sort_keys=True))\n"
        )
        self.assertEqual("completed", outcome["status"])
        self.assertEqual(b'{"value": "execution-main"}\n', b"".join(chunk for _, chunk in outcome["output"]))

    def test_representative_stdlib_import_matrix(self) -> None:
        outcome = run(
            b"import asyncio, collections, datetime, decimal, fractions, importlib, json, math, pathlib, re\n"
            b"print('stdlib-ok', math.isfinite(decimal.Decimal('1.0')))\n"
        )
        self.assertEqual("completed", outcome["status"])
        self.assertEqual(b"stdlib-ok True\n", b"".join(chunk for _, chunk in outcome["output"]))

    def test_missing_third_party_package_is_standard_module_not_found(self) -> None:
        outcome = run(b"import autojs6_u1_package_which_does_not_exist\n")
        self.assertEqual("failed", outcome["status"])
        self.assertEqual("ModuleNotFoundError", outcome["exception_type"])

    def test_stdio_argv_and_import_state_are_restored(self) -> None:
        stdin, stdout, stderr, argv = sys.stdin, sys.stdout, sys.stderr, sys.argv
        path_object, path = sys.path, list(sys.path)
        modules_object, modules = sys.modules, dict(sys.modules)
        importer_cache_object, importer_cache = sys.path_importer_cache, dict(sys.path_importer_cache)
        run(
            b"import sys\n"
            b"sys.path = ['poison']\n"
            b"sys.modules = {'poison': object()}\n"
            b"sys.path_importer_cache = {'poison': None}\n",
            stdin=b"unused",
        )
        self.assertIs(stdin, sys.stdin)
        self.assertIs(stdout, sys.stdout)
        self.assertIs(stderr, sys.stderr)
        self.assertIs(argv, sys.argv)
        self.assertIs(path_object, sys.path)
        self.assertEqual(path, sys.path)
        self.assertIs(modules_object, sys.modules)
        self.assertEqual(modules, sys.modules)
        self.assertIs(importer_cache_object, sys.path_importer_cache)
        self.assertEqual(importer_cache, sys.path_importer_cache)

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

    def test_project_package_entry_supports_relative_import_and_cleans_module_cache(self) -> None:
        previous_modules = dict(sys.modules)
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            source = b"from .helper import VALUE\nprint(VALUE, __package__)\n"
            (root / "pkg").mkdir()
            (root / "pkg" / "__init__.py").write_text("", encoding="utf-8")
            (root / "pkg" / "main.py").write_bytes(source)
            (root / "pkg" / "helper.py").write_text("VALUE = 'relative'\n", encoding="utf-8")

            outcome = run_project(source, "pkg/main.py", str(root), [], 4096, 64, 128)

        self.assertEqual("completed", outcome["status"])
        self.assertEqual(b"relative pkg\n", b"".join(chunk for _, chunk in outcome["output"]))
        self.assertEqual(previous_modules, sys.modules)

    def test_sequential_projects_do_not_reuse_same_named_module(self) -> None:
        outputs: list[bytes] = []
        for value in ("first", "second"):
            with tempfile.TemporaryDirectory() as directory:
                root = pathlib.Path(directory)
                source = b"import shared_name\nprint(shared_name.VALUE)\n"
                (root / "main.py").write_bytes(source)
                (root / "shared_name.py").write_text(
                    f"VALUE = {value!r}\n",
                    encoding="utf-8",
                )
                outcome = run_project(source, "main.py", str(root), [], 4096, 64, 128)
                self.assertEqual("completed", outcome["status"])
                outputs.append(b"".join(chunk for _, chunk in outcome["output"]))
        self.assertEqual([b"first\n", b"second\n"], outputs)

    def test_project_reexport_and_circular_import(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            source = b"from pkg import exported\nprint(exported())\n"
            (root / "main.py").write_bytes(source)
            (root / "pkg").mkdir()
            (root / "pkg" / "__init__.py").write_text(
                "from .left import exported\n",
                encoding="utf-8",
            )
            (root / "pkg" / "left.py").write_text(
                "from . import right\ndef exported(): return 'cycle-' + right.VALUE\n",
                encoding="utf-8",
            )
            (root / "pkg" / "right.py").write_text("VALUE = 'ok'\n", encoding="utf-8")
            outcome = run_project(source, "main.py", str(root), [], 4096, 64, 128)
        self.assertEqual("completed", outcome["status"])
        self.assertEqual(b"cycle-ok\n", b"".join(chunk for _, chunk in outcome["output"]))


if __name__ == "__main__":
    unittest.main()
