from __future__ import annotations

import builtins
import getpass
import json
import pathlib
import os
import sys
import tempfile
import threading
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
    output_sink=None,
    input_bridge=None,
    output_artifact_root: str | None = None,
    max_structured_json_bytes: int = 0,
    max_output_artifacts: int = 0,
    max_output_artifact_path_bytes: int = 0,
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
        output_sink,
        input_bridge,
        output_artifact_root,
        max_structured_json_bytes,
        max_output_artifacts,
        max_output_artifact_path_bytes,
    )


class RecordingOutputSink:
    def __init__(self) -> None:
        self.records: list[tuple[str, bytes]] = []

    def emit(self, stream: str, payload: bytes) -> bool:
        self.records.append((stream, bytes(payload)))
        return True


class RecordingInputBridge:
    def __init__(self, *responses: str) -> None:
        self.responses = list(responses)
        self.calls: list[tuple[str, str]] = []

    def request(self, prompt: str, echo: str) -> str:
        self.calls.append((prompt, echo))
        if not self.responses:
            raise AssertionError("unexpected interactive input request")
        return self.responses.pop(0)


class BootstrapTest(unittest.TestCase):
    def test_explicit_structured_json_is_canonical_and_never_inferred_from_stdout(self) -> None:
        outcome = run(
            "from autojs6 import result\n"
            "print('{\\\"stdoutOnly\\\":true}')\n"
            "result.set({'z': 1, 'message': '你好', 'items': [True, None, 2.5]})\n".encode("utf-8"),
            max_structured_json_bytes=1024,
        )

        self.assertEqual("completed", outcome["status"])
        self.assertEqual(
            '{"items":[true,null,2.5],"message":"你好","z":1}',
            outcome["structured_json"],
        )
        self.assertEqual(b'{"stdoutOnly":true}\n', b"".join(chunk for _, chunk in outcome["output"]))
        self.assertNotEqual(
            outcome["structured_json"],
            b"".join(chunk for _, chunk in outcome["output"]).decode("utf-8").strip(),
        )

    def test_structured_result_is_single_assignment_strict_and_bounded(self) -> None:
        cases = (
            (b"from autojs6 import result\nresult.set(float('nan'))\n", "ResultSerializationError", 64),
            (b"from autojs6 import result\nresult.set({1: 'not-a-string-key'})\n", "ResultSerializationError", 64),
            (b"from autojs6 import result\nresult.set('first')\nresult.set('second')\n", "ResultAlreadySetError", 64),
            (b"from autojs6 import result\nresult.set('too-large')\n", "ResultLimitError", 4),
        )
        for source, expected, maximum in cases:
            with self.subTest(expected=expected):
                outcome = run(source, max_structured_json_bytes=maximum)
                self.assertEqual("failed", outcome["status"])
                self.assertEqual(expected, outcome["exception_type"])
                self.assertIsNone(outcome["structured_json"])

    def test_output_artifact_paths_are_explicit_normalized_and_execution_scoped(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            outcome = run(
                b"from pathlib import Path\n"
                b"from autojs6 import artifacts\n"
                b"first = artifacts.path('reports/result.bin')\n"
                b"assert artifacts.path('reports/result.bin') == first\n"
                b"Path(first).write_bytes(b'artifact-data')\n",
                output_artifact_root=directory,
                max_output_artifacts=2,
                max_output_artifact_path_bytes=128,
            )
            self.assertEqual(b"artifact-data", (pathlib.Path(directory) / "reports/result.bin").read_bytes())

        self.assertEqual("completed", outcome["status"])
        self.assertEqual(("reports/result.bin",), outcome["artifact_paths"])
        self.assertIsNone(outcome["structured_json"])

    def test_output_artifact_path_and_count_limits_fail_closed(self) -> None:
        unsafe_paths = ("", "/absolute", "C:/absolute", "dir\\file", "./file", "../file", "a//b")
        for unsafe in unsafe_paths:
            with self.subTest(unsafe=unsafe), tempfile.TemporaryDirectory() as directory:
                source = f"from autojs6 import artifacts\nartifacts.path({unsafe!r})\n".encode("utf-8")
                outcome = run(
                    source,
                    output_artifact_root=directory,
                    max_output_artifacts=2,
                    max_output_artifact_path_bytes=128,
                )
                self.assertEqual("failed", outcome["status"])
                self.assertEqual("ArtifactPathError", outcome["exception_type"])

        with tempfile.TemporaryDirectory() as directory:
            count = run(
                b"from autojs6 import artifacts\nartifacts.path('one')\nartifacts.path('two')\n",
                output_artifact_root=directory,
                max_output_artifacts=1,
                max_output_artifact_path_bytes=128,
            )
        self.assertEqual("failed", count["status"])
        self.assertEqual("ArtifactLimitError", count["exception_type"])

    def test_explicit_result_apis_are_unavailable_without_a_negotiated_policy(self) -> None:
        for source in (
            b"from autojs6 import result\nresult.set({'not': 'authorized'})\n",
            b"from autojs6 import artifacts\nartifacts.path('not-authorized')\n",
        ):
            outcome = run(source)
            self.assertEqual("failed", outcome["status"])
            self.assertEqual("CapabilityUnavailableError", outcome["exception_type"])
            self.assertIsNone(outcome["structured_json"])
            self.assertEqual((), outcome["artifact_paths"])

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

    def test_execution_time_sink_receives_ordered_chunks_without_result_buffering(self) -> None:
        sink = RecordingOutputSink()
        outcome = run(
            b"import sys\n"
            b"sys.stdout.write('out')\n"
            b"sys.stderr.write('err')\n"
            b"sys.stdout.buffer.write(b'012345')\n",
            maximum_chunk=4,
            output_sink=sink,
        )

        self.assertEqual("completed", outcome["status"])
        self.assertEqual((), outcome["output"])
        self.assertEqual(
            [
                ("stdout", b"out"),
                ("stderr", b"err"),
                ("stdout", b"0123"),
                ("stdout", b"45"),
            ],
            sink.records,
        )

    def test_execution_blocks_inside_sink_until_backpressure_is_released(self) -> None:
        entered = threading.Event()
        release = threading.Event()
        result: dict[str, object] = {}

        class BlockingSink(RecordingOutputSink):
            def emit(self, stream: str, payload: bytes) -> bool:
                entered.set()
                if not release.wait(2.0):
                    return False
                return super().emit(stream, payload)

        sink = BlockingSink()

        def execute() -> None:
            result["outcome"] = run(
                b"import sys\nsys.stdout.write('blocked')\n",
                output_sink=sink,
            )

        thread = threading.Thread(target=execute, daemon=True)
        thread.start()
        try:
            self.assertTrue(entered.wait(2.0))
            self.assertTrue(thread.is_alive())
        finally:
            release.set()
        thread.join(2.0)

        self.assertFalse(thread.is_alive())
        self.assertEqual("completed", result["outcome"]["status"])
        self.assertEqual([("stdout", b"blocked")], sink.records)

    def test_sink_stop_preserves_prior_output_and_stops_user_code(self) -> None:
        class StopAfterFirstSink(RecordingOutputSink):
            def __init__(self) -> None:
                super().__init__()
                self.attempts = 0

            def emit(self, stream: str, payload: bytes) -> bool:
                self.attempts += 1
                if self.attempts > 1:
                    return False
                return super().emit(stream, payload)

        sink = StopAfterFirstSink()
        outcome = run(
            b"import sys\n"
            b"sys.stdout.write('before')\n"
            b"sys.stderr.write('stop-here')\n"
            b"sys.stdout.write('after')\n",
            output_sink=sink,
        )

        self.assertEqual("stopped", outcome["status"])
        self.assertEqual(2, sink.attempts)
        self.assertEqual([("stdout", b"before")], sink.records)
        self.assertEqual((), outcome["output"])

    def test_streaming_output_limit_preserves_already_delivered_chunks(self) -> None:
        sink = RecordingOutputSink()
        outcome = run(
            b"import sys\n"
            b"sys.stdout.write('ab')\n"
            b"sys.stderr.write('cd')\n",
            maximum_bytes=3,
            maximum_chunk=2,
            output_sink=sink,
        )

        self.assertEqual("output_limit", outcome["status"])
        self.assertEqual([("stdout", b"ab")], sink.records)
        self.assertEqual((), outcome["output"])

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

    def test_interactive_input_consumes_snapshot_before_requesting_live_replies(self) -> None:
        bridge = RecordingInputBridge("\u0001live")
        outcome = run(
            b"first = input('first>')\n"
            b"second = input('second>')\n"
            b"print(first, second, sep='/')\n",
            stdin=b"snapshot\n",
            input_bridge=bridge,
        )

        self.assertEqual("completed", outcome["status"])
        self.assertEqual(b"first>second>snapshot/live\n", b"".join(chunk for _, chunk in outcome["output"]))
        self.assertEqual([("second>", "visible")], bridge.calls)

    def test_interactive_input_supports_multiple_prompts_empty_values_eof_and_cancel(self) -> None:
        values = RecordingInputBridge("\u0001Ada", "\u0001")
        completed = run(
            b"print(repr(input('name>')), repr(input('empty>')))\n",
            input_bridge=values,
        )
        self.assertEqual("completed", completed["status"])
        self.assertEqual(b"name>empty>'Ada' ''\n", b"".join(chunk for _, chunk in completed["output"]))
        self.assertEqual(
            [("name>", "visible"), ("empty>", "visible")],
            values.calls,
        )

        eof_bridge = RecordingInputBridge("\u0002")
        eof = run(b"input('eof>')\n", input_bridge=eof_bridge)
        self.assertEqual("failed", eof["status"])
        self.assertEqual("EOFError", eof["exception_type"])
        self.assertEqual(b"eof>", b"".join(chunk for _, chunk in eof["output"]))

        cancel_bridge = RecordingInputBridge("\u0003")
        cancelled = run(b"input('cancel>')\n", input_bridge=cancel_bridge)
        self.assertEqual("failed", cancelled["status"])
        self.assertEqual("KeyboardInterrupt", cancelled["exception_type"])
        self.assertEqual(b"cancel>", b"".join(chunk for _, chunk in cancelled["output"]))

    def test_getpass_consumes_snapshot_then_uses_hidden_echo_and_restores_function(self) -> None:
        original_getpass = getpass.getpass
        bridge = RecordingInputBridge("\u0001live-secret")
        outcome = run(
            b"from getpass import getpass\n"
            b"first = getpass('snapshot-secret>')\n"
            b"second = getpass('live-secret>')\n"
            b"print(first, second, sep='/')\n",
            stdin=b"snapshot-secret\n",
            input_bridge=bridge,
        )

        self.assertEqual("completed", outcome["status"])
        self.assertEqual(
            b"snapshot-secret>live-secret>snapshot-secret/live-secret\n",
            b"".join(chunk for _, chunk in outcome["output"]),
        )
        self.assertEqual([("live-secret>", "hidden")], bridge.calls)
        self.assertIs(original_getpass, getpass.getpass)

    def test_getpass_maps_hidden_eof_and_cancel_to_python_control_flow(self) -> None:
        for marker, expected in (("\u0002", "EOFError"), ("\u0003", "KeyboardInterrupt")):
            with self.subTest(expected=expected):
                bridge = RecordingInputBridge(marker)
                outcome = run(
                    b"import getpass\ngetpass.getpass('password>')\n",
                    input_bridge=bridge,
                )

                self.assertEqual("failed", outcome["status"])
                self.assertEqual(expected, outcome["exception_type"])
                self.assertEqual(b"password>", b"".join(chunk for _, chunk in outcome["output"]))
                self.assertEqual([("password>", "hidden")], bridge.calls)

    def test_interactive_bridge_does_not_turn_sys_stdin_reads_into_an_unbounded_stream(self) -> None:
        bridge = RecordingInputBridge("\u0001must-not-be-consumed")
        outcome = run(
            b"import sys\nprint(repr(sys.stdin.readline()), repr(sys.stdin.read()))\n",
            input_bridge=bridge,
        )

        self.assertEqual("completed", outcome["status"])
        self.assertEqual(b"'' ''\n", b"".join(chunk for _, chunk in outcome["output"]))
        self.assertEqual([], bridge.calls)

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
        builtin_input = builtins.input
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
        self.assertIs(builtin_input, builtins.input)
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

    def test_file_and_module_modes_have_distinct_main_metadata_and_path_zero(self) -> None:
        previous_modules = dict(sys.modules)
        previous_path = list(sys.path)
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            package = root / "pkg"
            package.mkdir()
            (package / "__init__.py").write_text("", encoding="utf-8")
            (package / "helper.py").write_text("VALUE = 'relative'\n", encoding="utf-8")
            source = (
                b"import json, os, sys\n"
                b"from .helper import VALUE\n"
                b"print(json.dumps({\n"
                b"    'argv0': sys.argv[0],\n"
                b"    'file': __file__,\n"
                b"    'name': __name__,\n"
                b"    'package': __package__,\n"
                b"    'path0': sys.path[0],\n"
                b"    'spec': None if __spec__ is None else __spec__.name,\n"
                b"    'value': VALUE,\n"
                b"}, sort_keys=True))\n"
            )
            entry_file = package / "main.py"
            entry_file.write_bytes(source)

            file_outcome = run_project(
                source,
                "pkg/main.py",
                str(root),
                [],
                4096,
                4096,
                128,
                entry_mode="file",
            )
            module_outcome = run_project(
                source,
                "pkg.main",
                str(root),
                [],
                4096,
                4096,
                128,
                entry_mode="module",
            )

            file_metadata = json.loads(b"".join(chunk for _, chunk in file_outcome["output"]))
            module_metadata = json.loads(b"".join(chunk for _, chunk in module_outcome["output"]))

            self.assertEqual("completed", file_outcome["status"])
            self.assertEqual("__main__", file_metadata["name"])
            self.assertEqual("pkg", file_metadata["package"])
            self.assertIsNone(file_metadata["spec"])
            self.assertEqual(str(package.resolve()), file_metadata["path0"])
            self.assertEqual("pkg/main.py", file_metadata["argv0"])
            self.assertEqual("pkg/main.py", file_metadata["file"])

            self.assertEqual("completed", module_outcome["status"])
            self.assertEqual("__main__", module_metadata["name"])
            self.assertEqual("pkg", module_metadata["package"])
            self.assertEqual("pkg.main", module_metadata["spec"])
            self.assertEqual(str(root.resolve()), module_metadata["path0"])
            self.assertEqual(str(entry_file.resolve()), module_metadata["argv0"])
            self.assertEqual(str(entry_file.resolve()), module_metadata["file"])
            self.assertEqual("relative", module_metadata["value"])

        for name, module in previous_modules.items():
            self.assertIs(module, sys.modules.get(name))
        self.assertNotIn("pkg", sys.modules)
        self.assertNotIn("pkg.helper", sys.modules)
        self.assertNotIn("pkg.main", sys.modules)
        self.assertEqual(previous_path, sys.path)

    def test_module_mode_rejects_source_mismatch_and_sanitizes_traceback_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            package = root / "pkg"
            package.mkdir()
            (package / "__init__.py").write_text("", encoding="utf-8")
            entry_file = package / "main.py"
            entry_file.write_text("raise RuntimeError('private module failure')\n", encoding="utf-8")

            mismatch = run_project(
                b"print('different')\n",
                "pkg.main",
                str(root),
                [],
                4096,
                64,
                128,
                entry_mode="module",
            )
            failure = run_project(
                entry_file.read_bytes(),
                "pkg.main",
                str(root),
                [],
                4096,
                64,
                128,
                entry_mode="module",
            )

        self.assertEqual("failed", mismatch["status"])
        self.assertEqual("ValueError", mismatch["exception_type"])
        self.assertEqual("failed", failure["status"])
        self.assertEqual("RuntimeError", failure["exception_type"])
        project_names = [
            frame["file_name"] for frame in failure["traceback"] if frame["origin"] == "project"
        ]
        self.assertIn("pkg/main.py", project_names)
        self.assertNotIn(str(root), repr(failure["traceback"]))

    def test_module_mode_isolates_a_preloaded_stdlib_name_and_restores_it(self) -> None:
        previous_json = sys.modules["json"]
        previous_json_modules = {
            name: module
            for name, module in sys.modules.items()
            if name == "json" or name.startswith("json.")
        }
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            source = b"print(__spec__.name, 'project-json')\n"
            (root / "json.py").write_bytes(source)

            outcome = run_project(
                source,
                "json",
                str(root),
                [],
                4096,
                64,
                128,
                entry_mode="module",
            )

        self.assertEqual("completed", outcome["status"])
        self.assertEqual(b"json project-json\n", b"".join(chunk for _, chunk in outcome["output"]))
        self.assertIs(previous_json, sys.modules["json"])
        for name, module in previous_json_modules.items():
            self.assertIs(module, sys.modules.get(name))

    def test_unknown_project_entry_mode_fails_before_user_code(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            source = b"print('must not run')\n"
            (root / "main.py").write_bytes(source)
            outcome = run_project(
                source,
                "main.py",
                str(root),
                [],
                4096,
                64,
                128,
                entry_mode="implicit",
            )

        self.assertEqual("failed", outcome["status"])
        self.assertEqual("ValueError", outcome["exception_type"])
        self.assertEqual([], list(outcome["output"]))

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
