"""Execute one bounded source snapshot without injecting host-side Java objects.

This is transport containment, not a security sandbox. Chaquopy exposes its own
Java bridge to Python code, so the Android process/UID and permission boundary
remain the effective isolation mechanism for the R2 POC.
"""

from __future__ import annotations

import io
import keyword
import linecache
import os
import re
import sys
import traceback as traceback_module
from dataclasses import dataclass
from types import ModuleType
from typing import Any

from autojs6._context import _install_execution_context, _reset_execution_context


class _OutputLimitExceeded(BaseException):
    pass


_MAX_STDIN_BYTES = 1024 * 1024
_SOURCE_CODING_COOKIE = re.compile(
    r"^[\t\f ]*#.*?coding[:=][\t ]*([-_.a-zA-Z0-9]+)",
    re.IGNORECASE,
)
_UTF8_CODING_NAMES = frozenset(("utf8", "utf-8", "utf-8-sig"))


@dataclass
class _OutputBudget:
    maximum_bytes: int
    maximum_chunk_bytes: int
    maximum_chunks: int
    total_bytes: int = 0
    total_chunks: int = 0

    def account(self, size: int) -> None:
        if size <= 0:
            return
        if self.total_bytes + size > self.maximum_bytes:
            raise _OutputLimitExceeded()
        if self.total_chunks + 1 > self.maximum_chunks:
            raise _OutputLimitExceeded()
        self.total_bytes += size
        self.total_chunks += 1


class _CaptureBuffer:
    def __init__(self, stream: str, budget: _OutputBudget, records: list[tuple[str, bytes]]) -> None:
        self._stream = stream
        self._budget = budget
        self._records = records

    def write(self, value: Any) -> int:
        payload = bytes(value)
        original_size = len(payload)
        for offset in range(0, original_size, self._budget.maximum_chunk_bytes):
            chunk = payload[offset : offset + self._budget.maximum_chunk_bytes]
            if chunk:
                self._budget.account(len(chunk))
                self._records.append((self._stream, chunk))
        return original_size

    def flush(self) -> None:
        return None


class _CaptureText:
    encoding = "utf-8"
    errors = "replace"

    def __init__(self, stream: str, budget: _OutputBudget, records: list[tuple[str, bytes]]) -> None:
        self.buffer = _CaptureBuffer(stream, budget, records)

    def write(self, value: Any) -> int:
        text = value if isinstance(value, str) else str(value)
        self.buffer.write(text.encode(self.encoding, self.errors))
        return len(text)

    def flush(self) -> None:
        return None

    def isatty(self) -> bool:
        return False

    def writable(self) -> bool:
        return True


def _bounded_exit_code(code: Any, stderr: _CaptureText) -> int:
    if code is None:
        return 0
    if isinstance(code, int) and 0 <= code <= 255:
        return int(code)
    stderr.write(f"{code}\n")
    return 1


def _decode_source(source_input: Any) -> str:
    """Decode the protocol source snapshot without honoring non-UTF-8 cookies."""
    source = bytes(source_input).decode("utf-8-sig", "strict")
    if "\x00" in source:
        raise ValueError("Python source contains a NUL byte")
    for line in source.splitlines()[:2]:
        match = _SOURCE_CODING_COOKIE.match(line)
        if match is None:
            continue
        encoding = match.group(1).lower().replace("_", "-")
        if encoding not in _UTF8_CODING_NAMES:
            raise ValueError("Python source declares a non-UTF-8 encoding")
    return source


def _stdin_snapshot(stdin_input: Any) -> io.TextIOWrapper:
    payload = bytes(stdin_input)
    if len(payload) > _MAX_STDIN_BYTES:
        raise ValueError("Python stdin snapshot exceeds the protocol limit")
    return io.TextIOWrapper(
        io.BytesIO(payload),
        encoding="utf-8",
        errors="strict",
        newline=None,
    )


def _entry_package(logical_entry: str, workspace_root: str | None) -> str | None:
    if workspace_root is None:
        return None
    parent_segments = logical_entry.split("/")[:-1]
    if not parent_segments or any(
        not segment.isidentifier() or keyword.iskeyword(segment)
        for segment in parent_segments
    ):
        return None
    return ".".join(parent_segments)


def _restore_modules(
    original: dict[str, Any],
    snapshot: dict[str, Any],
    workspace_root: str | None,
) -> None:
    sys.modules = original
    for name, value in snapshot.items():
        original[name] = value
    for name in tuple(set(original) - set(snapshot)):
        module_file = getattr(original.get(name), "__file__", None)
        if name == "__main__" or (
            isinstance(module_file, str)
            and _project_relative(module_file, workspace_root) is not None
        ):
            original.pop(name, None)


def _restore_importer_cache(
    original: dict[Any, Any],
    snapshot: dict[Any, Any],
    workspace_root: str | None,
) -> None:
    sys.path_importer_cache = original
    for path, value in snapshot.items():
        original[path] = value
    for path in tuple(set(original) - set(snapshot)):
        try:
            within_workspace = _is_within_workspace(os.fspath(path), workspace_root)
        except TypeError:
            within_workspace = False
        if within_workspace:
            original.pop(path, None)


def _safe_relative_leaf(prefix: str, filename: str) -> str:
    leaf = os.path.basename(filename.replace("\\", "/")) or "module.py"
    safe = "".join(character if character.isalnum() or character in "._-" else "_" for character in leaf)
    return f"{prefix}/{safe or 'module.py'}"


def _is_within_workspace(filename: str, workspace_root: str | None) -> bool:
    if workspace_root is None or (filename.startswith("<") and filename.endswith(">")):
        return False
    try:
        candidate = filename if os.path.isabs(filename) else os.path.join(workspace_root, filename)
        resolved = os.path.realpath(candidate)
        return os.path.commonpath((workspace_root, resolved)) == workspace_root
    except (OSError, ValueError):
        return False


def _project_relative(filename: str, workspace_root: str | None) -> str | None:
    if not _is_within_workspace(filename, workspace_root):
        return None
    try:
        candidate = filename if os.path.isabs(filename) else os.path.join(workspace_root, filename)
        resolved = os.path.realpath(candidate)
        relative = os.path.relpath(resolved, workspace_root).replace(os.sep, "/")
        return relative if relative != "." else None
    except (OSError, ValueError):
        return None


def _frame_origin(
    filename: str,
    logical_entry: str,
    workspace_root: str | None,
) -> tuple[str, str]:
    if filename == logical_entry:
        return "project", logical_entry
    project_relative = _project_relative(filename, workspace_root)
    if project_relative is not None:
        return "project", project_relative
    if filename.startswith("<") and filename.endswith(">"):
        synthetic = filename.replace("/", "_").replace("\\", "_")
        return "generated", synthetic
    normalized = filename.replace("\\", "/")
    if "/site-packages/" in normalized or "/chaquopy/" in normalized:
        return "package", _safe_relative_leaf("package", filename)
    return "stdlib", _safe_relative_leaf("stdlib", filename)


def _traceback_frames(
    error: BaseException,
    logical_entry: str,
    workspace_root: str | None,
) -> list[dict[str, Any]]:
    frames: list[dict[str, Any]] = []
    extracted = traceback_module.extract_tb(error.__traceback__)
    if isinstance(error, SyntaxError):
        filename = error.filename or logical_entry
        syntax_frame = traceback_module.FrameSummary(
            filename,
            max(1, int(error.lineno or 1)),
            "<module>",
            line=(error.text or "").strip("\r\n"),
        )
        if not any(frame.filename == filename and frame.lineno == syntax_frame.lineno for frame in extracted):
            extracted.append(syntax_frame)
    for frame in extracted[-256:]:
        origin, safe_name = _frame_origin(frame.filename, logical_entry, workspace_root)
        source_line = frame.line
        if source_line is None and frame.filename == logical_entry:
            source_line = linecache.getline(frame.filename, frame.lineno).strip("\r\n") or None
        frames.append(
            {
                "origin": origin,
                "file_name": safe_name,
                "line_number": max(1, int(frame.lineno)),
                "function_name": frame.name or "<module>",
                "source_line": source_line,
            }
        )
    return frames


def _run_source(
    source_input: Any,
    logical_entry: str,
    arguments: list[str],
    maximum_output_bytes: int,
    maximum_output_chunk_bytes: int,
    maximum_output_chunks: int,
    workspace_root: str | None,
    host_capability_snapshot_input: Any,
    stdin_input: Any,
) -> dict[str, Any]:
    records: list[tuple[str, bytes]] = []
    budget = _OutputBudget(
        int(maximum_output_bytes),
        int(maximum_output_chunk_bytes),
        int(maximum_output_chunks),
    )
    stdout = _CaptureText("stdout", budget, records)
    stderr = _CaptureText("stderr", budget, records)
    stdin: io.TextIOWrapper | None = None
    previous_stdin, previous_stdout, previous_stderr, previous_argv = (
        sys.stdin,
        sys.stdout,
        sys.stderr,
        sys.argv,
    )
    previous_cwd = os.getcwd()
    previous_sys_path_object = sys.path
    previous_sys_path = list(previous_sys_path_object)
    previous_modules_object = sys.modules
    previous_modules = dict(previous_modules_object)
    previous_importer_cache_object = sys.path_importer_cache
    previous_importer_cache = dict(previous_importer_cache_object)
    capability_token: Any = None
    main_module = ModuleType("__main__")
    globals_dict = main_module.__dict__
    globals_dict.update({
        "__name__": "__main__",
        "__file__": logical_entry,
        "__package__": _entry_package(logical_entry, workspace_root),
        "__cached__": None,
        "__builtins__": __builtins__,
    })
    try:
        source = _decode_source(source_input)
        source_input = None
        stdin = _stdin_snapshot(stdin_input)
        stdin_input = None
        host_capability_snapshot = bytes(host_capability_snapshot_input)
        host_capability_snapshot_input = None
        if workspace_root is not None:
            workspace_root = os.path.realpath(os.fspath(workspace_root))
            if not os.path.isdir(workspace_root):
                raise ValueError("Python project workspace is unavailable")
            entry_file = os.path.realpath(os.path.join(workspace_root, *logical_entry.split("/")))
            if os.path.commonpath((workspace_root, entry_file)) != workspace_root or not os.path.isfile(entry_file):
                raise ValueError("Python project entry point is unavailable")
            entry_directory = os.path.dirname(entry_file)
            project_paths = [entry_directory]
            if entry_directory != workspace_root:
                project_paths.append(workspace_root)
            project_path_keys = {os.path.normcase(os.path.realpath(path)) for path in project_paths}
            retained_sys_path = []
            for path in previous_sys_path:
                try:
                    key = os.path.normcase(os.path.realpath(os.fspath(path)))
                except (OSError, TypeError, ValueError):
                    retained_sys_path.append(path)
                    continue
                if key not in project_path_keys:
                    retained_sys_path.append(path)
            os.chdir(workspace_root)
            sys.path[:] = [*project_paths, *retained_sys_path]
        capability_token = _install_execution_context(host_capability_snapshot, workspace_root)
        host_capability_snapshot = None
        sys.stdin, sys.stdout, sys.stderr = stdin, stdout, stderr
        sys.argv = [logical_entry, *list(arguments)]
        sys.modules["__main__"] = main_module
        code = compile(source, logical_entry, "exec", dont_inherit=True)
        try:
            exec(code, globals_dict, globals_dict)
            exit_code = 0
        except SystemExit as exit_signal:
            exit_code = _bounded_exit_code(exit_signal.code, stderr)
        return {
            "status": "completed",
            "exit_code": exit_code,
            "output": tuple(records),
            "traceback": [],
            "exception_type": "",
            "exception_message": "",
        }
    except _OutputLimitExceeded:
        return {
            "status": "output_limit",
            "exit_code": 1,
            "output": tuple(records),
            "traceback": [],
            "exception_type": "",
            "exception_message": "",
        }
    except BaseException as error:
        return {
            "status": "failed",
            "exit_code": 1,
            "output": tuple(records),
            "traceback": _traceback_frames(error, logical_entry, workspace_root),
            "exception_type": type(error).__name__,
            "exception_message": str(error),
        }
    finally:
        if capability_token is not None:
            _reset_execution_context(capability_token)
        sys.stdin, sys.stdout, sys.stderr, sys.argv = (
            previous_stdin,
            previous_stdout,
            previous_stderr,
            previous_argv,
        )
        sys.path = previous_sys_path_object
        previous_sys_path_object[:] = previous_sys_path
        _restore_importer_cache(
            previous_importer_cache_object,
            previous_importer_cache,
            workspace_root,
        )
        _restore_modules(previous_modules_object, previous_modules, workspace_root)
        os.chdir(previous_cwd)
        if stdin is not None:
            try:
                stdin.close()
            except (OSError, ValueError):
                pass
        linecache.clearcache()
        globals_dict.clear()


def run_source(
    source_input: Any,
    logical_entry: str,
    arguments: list[str],
    maximum_output_bytes: int,
    maximum_output_chunk_bytes: int,
    maximum_output_chunks: int,
    host_capability_snapshot_input: Any = b"",
    stdin_input: Any = b"",
) -> dict[str, Any]:
    return _run_source(
        source_input,
        logical_entry,
        arguments,
        maximum_output_bytes,
        maximum_output_chunk_bytes,
        maximum_output_chunks,
        None,
        host_capability_snapshot_input,
        stdin_input,
    )


def run_project(
    source_input: Any,
    logical_entry: str,
    workspace_root: str,
    arguments: list[str],
    maximum_output_bytes: int,
    maximum_output_chunk_bytes: int,
    maximum_output_chunks: int,
    host_capability_snapshot_input: Any = b"",
    stdin_input: Any = b"",
) -> dict[str, Any]:
    return _run_source(
        source_input,
        logical_entry,
        arguments,
        maximum_output_bytes,
        maximum_output_chunk_bytes,
        maximum_output_chunks,
        workspace_root,
        host_capability_snapshot_input,
        stdin_input,
    )


__all__ = ("run_project", "run_source")
