"""Bounded read-only convenience access to the private project snapshot."""

from __future__ import annotations

import os
import re
import stat
import unicodedata

from ._context import _project_context
from .errors import ProjectPathError, ProjectReadLimitError


MAX_READ_BYTES = 1024 * 1024
_MAX_PATH_BYTES = 4096
_WINDOWS_DRIVE = re.compile(r"^[A-Za-z]:")


def read_bytes(path: str | os.PathLike[str]) -> bytes:
    """Read at most 1 MiB from one regular file in the frozen project workspace."""
    descriptor = _open_regular(path)
    try:
        with os.fdopen(descriptor, "rb", closefd=True) as stream:
            payload = stream.read(MAX_READ_BYTES + 1)
    except BaseException:
        try:
            os.close(descriptor)
        except OSError:
            pass
        raise
    if len(payload) > MAX_READ_BYTES:
        raise ProjectReadLimitError(
            f"Project file exceeds the {MAX_READ_BYTES}-byte per-call read limit"
        )
    return payload


def read_text(path: str | os.PathLike[str], *, encoding: str = "utf-8") -> str:
    """Read one UTF-8 project file with strict decoding and the same 1 MiB limit."""
    if encoding.lower().replace("_", "-") not in {"utf-8", "utf8"}:
        raise ValueError("The R5 preview project API supports UTF-8 text only")
    return read_bytes(path).decode("utf-8", "strict")


def exists(path: str | os.PathLike[str]) -> bool:
    """Return whether a safe project-relative path names a regular file."""
    try:
        descriptor = _open_regular(path)
    except (FileNotFoundError, NotADirectoryError):
        return False
    try:
        return True
    finally:
        os.close(descriptor)


def _open_regular(path: str | os.PathLike[str]) -> int:
    context = _project_context()
    relative = _normalize_relative(path)
    root = context.project_root
    assert root is not None
    try:
        if _supports_openat():
            descriptor = _openat_no_follow(root, relative)
        else:
            descriptor = _open_portable(root, relative)
    except (FileNotFoundError, NotADirectoryError):
        raise
    except OSError as error:
        raise ProjectPathError("Project path could not be opened safely") from error
    opened = os.fstat(descriptor)
    if not stat.S_ISREG(opened.st_mode):
        os.close(descriptor)
        raise ProjectPathError("Project path must name a regular file")
    return descriptor


def _openat_no_follow(root: str, relative: str) -> int:
    directory_flags = (
        os.O_RDONLY
        | os.O_CLOEXEC
        | os.O_NOFOLLOW
        | os.O_DIRECTORY
        | getattr(os, "O_NONBLOCK", 0)
    )
    file_flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | getattr(os, "O_NONBLOCK", 0)
    current = os.open(root, directory_flags)
    try:
        segments = relative.split("/")
        for segment in segments[:-1]:
            following = os.open(segment, directory_flags, dir_fd=current)
            os.close(current)
            current = following
        return os.open(segments[-1], file_flags, dir_fd=current)
    finally:
        os.close(current)


def _open_portable(root: str, relative: str) -> int:
    canonical_root = os.path.realpath(root)
    candidate = os.path.realpath(os.path.join(canonical_root, *relative.split("/")))
    try:
        within = os.path.commonpath((canonical_root, candidate)) == canonical_root
    except ValueError as error:
        raise ProjectPathError("Project path escapes the private workspace") from error
    if not within:
        raise ProjectPathError("Project path escapes the private workspace")
    before = os.lstat(candidate)
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode):
        raise ProjectPathError("Project path must name a regular non-link file")
    descriptor = os.open(candidate, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0))
    after = os.fstat(descriptor)
    if (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino):
        os.close(descriptor)
        raise ProjectPathError("Project path changed while it was opened")
    return descriptor


def _normalize_relative(path: str | os.PathLike[str]) -> str:
    value = os.fspath(path)
    if not isinstance(value, str):
        raise ProjectPathError("Project path must be text")
    if (
        not value
        or value.startswith("/")
        or _WINDOWS_DRIVE.match(value)
        or "\\" in value
        or any(ord(character) < 0x20 for character in value)
        or unicodedata.normalize("NFC", value) != value
        or len(value.encode("utf-8")) > _MAX_PATH_BYTES
    ):
        raise ProjectPathError("Project path must be a normalized project-relative path")
    segments = value.split("/")
    if any(not segment or segment in {".", ".."} for segment in segments):
        raise ProjectPathError("Project path contains an unsafe segment")
    return value


def _supports_openat() -> bool:
    return (
        os.open in getattr(os, "supports_dir_fd", set())
        and hasattr(os, "O_NOFOLLOW")
        and hasattr(os, "O_DIRECTORY")
        and hasattr(os, "O_CLOEXEC")
    )


__all__ = ("MAX_READ_BYTES", "exists", "read_bytes", "read_text")
