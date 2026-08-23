"""Bounded live access to the current script's Host-side directory."""

from __future__ import annotations

import builtins
import os
import re
import unicodedata

from ._broker import (
    _call,
    _expect_boolean,
    _expect_none,
    _expect_text,
    _protocol_error,
    _require_text,
)


MAX_PATH_BYTES = 4 * 1024
MAX_TEXT_BYTES = 32 * 1024
MAX_LIST_ENTRIES = 128
MAX_NAME_BYTES = 255
_ROOT_PATH = "."
_WINDOWS_DRIVE = re.compile(r"^[A-Za-z]:")


def read_text(
    path: str | os.PathLike[str],
    *,
    encoding: str = "utf-8",
) -> str:
    """Read one bounded UTF-8 file from the live Host execution root."""
    _require_utf8(encoding)
    relative = _normalize_path(path)
    value = _expect_text(_call("files.read_text", {"path": relative}), "files.read_text")
    try:
        size = len(value.encode("utf-8", "strict"))
    except UnicodeError as error:
        raise _protocol_error("files.read_text returned invalid UTF-8", error)
    if size > MAX_TEXT_BYTES:
        raise _protocol_error("files.read_text returned text beyond the byte limit")
    return value


def write_text(
    path: str | os.PathLike[str],
    text: str,
    *,
    encoding: str = "utf-8",
) -> None:
    """Overwrite one file in the live Host execution root without creating parents."""
    _require_utf8(encoding)
    relative = _normalize_path(path)
    value = _require_text(text, "Host file text", max_bytes=MAX_TEXT_BYTES)
    _expect_none(
        _call("files.write_text", {"path": relative, "text": value}),
        "files.write_text",
    )


def exists(path: str | os.PathLike[str]) -> bool:
    """Return whether one safe path currently exists in the Host execution root."""
    return _path_boolean("files.exists", path)


def is_file(path: str | os.PathLike[str]) -> bool:
    """Return whether one safe path is currently a regular Host-side file."""
    return _path_boolean("files.is_file", path)


def is_dir(path: str | os.PathLike[str]) -> bool:
    """Return whether one safe path is currently a Host-side directory."""
    return _path_boolean("files.is_dir", path)


def list(path: str | os.PathLike[str] = _ROOT_PATH) -> list[str]:
    """List at most 128 sorted direct child names from one Host-side directory."""
    relative = _normalize_path(path)
    value = _call("files.list", {"path": relative})
    if type(value) is not builtins.list:
        raise _protocol_error("files.list returned a non-list value")
    if len(value) > MAX_LIST_ENTRIES:
        raise _protocol_error("files.list returned too many entries")
    entries: list[str] = []
    for entry in value:
        if (
            type(entry) is not str
            or not entry
            or "/" in entry
            or "\\" in entry
            or any(unicodedata.category(character) == "Cc" for character in entry)
            or unicodedata.normalize("NFC", entry) != entry
        ):
            raise _protocol_error("files.list returned an invalid entry name")
        try:
            size = len(entry.encode("utf-8", "strict"))
        except UnicodeError as error:
            raise _protocol_error("files.list returned an invalid UTF-8 entry", error)
        if size > MAX_NAME_BYTES:
            raise _protocol_error("files.list returned an oversized entry name")
        entries.append(entry)
    if len(set(entries)) != len(entries):
        raise _protocol_error("files.list returned duplicate entries")
    return sorted(entries)


def _path_boolean(capability: str, path: str | os.PathLike[str]) -> bool:
    relative = _normalize_path(path)
    return _expect_boolean(_call(capability, {"path": relative}), capability)


def _normalize_path(path: str | os.PathLike[str]) -> str:
    value = os.fspath(path)
    if not isinstance(value, str):
        raise TypeError("Host file path must be text")
    try:
        size = len(value.encode("utf-8", "strict"))
    except UnicodeError as error:
        raise ValueError("Host file path must be valid UTF-8 text") from error
    if (
        not value
        or size > MAX_PATH_BYTES
        or (
            value != _ROOT_PATH
            and (
                value.startswith("/")
                or _WINDOWS_DRIVE.match(value)
                or "\\" in value
                or any(unicodedata.category(character) == "Cc" for character in value)
                or unicodedata.normalize("NFC", value) != value
                or any(segment in {"", ".", ".."} for segment in value.split("/"))
            )
        )
    ):
        raise ValueError("Host file path must be a normalized execution-relative path")
    return value


def _require_utf8(encoding: str) -> None:
    if not isinstance(encoding, str):
        raise TypeError("Host file encoding must be text")
    if encoding.lower().replace("_", "-") not in {"utf-8", "utf8"}:
        raise ValueError("The Host files API supports UTF-8 text only")


__all__ = (
    "MAX_LIST_ENTRIES",
    "MAX_PATH_BYTES",
    "MAX_TEXT_BYTES",
    "exists",
    "is_dir",
    "is_file",
    "list",
    "read_text",
    "write_text",
)
