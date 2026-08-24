"""Bounded text recognition through the AutoJs6 Host-selected OCR engine."""

from __future__ import annotations

from typing import Any, NoReturn

from ._broker import _call, _protocol_error
from .images import _uploaded_template


MAX_LINES = 256
MAX_LINE_BYTES = 4 * 1024
MAX_TOTAL_TEXT_BYTES = 48 * 1024


def recognize(image: bytes | bytearray | memoryview) -> tuple[str, ...]:
    """Recognize text in one bounded PNG/JPEG image using the configured Host OCR engine."""
    with _uploaded_template(image) as (template_id, _, _):
        return _recognized_lines(
            _call("ocr.recognize", {"templateId": template_id})
        )


def _recognized_lines(value: Any) -> tuple[str, ...]:
    if type(value) is not list:
        _invalid("ocr.recognize returned a non-list value")
    if len(value) > MAX_LINES:
        _invalid("ocr.recognize returned too many lines")
    result: list[str] = []
    total_bytes = 0
    for line in value:
        if type(line) is not str:
            _invalid("ocr.recognize returned a non-text line")
        try:
            line_bytes = len(line.encode("utf-8", "strict"))
        except UnicodeError as error:
            raise _protocol_error("ocr.recognize returned non-UTF-8 text", error)
        if line_bytes > MAX_LINE_BYTES:
            _invalid("ocr.recognize returned a line beyond the byte limit")
        total_bytes += line_bytes
        if total_bytes > MAX_TOTAL_TEXT_BYTES:
            _invalid("ocr.recognize returned text beyond the aggregate byte limit")
        result.append(line)
    return tuple(result)


def _invalid(message: str) -> NoReturn:
    raise _protocol_error(message)


__all__ = (
    "MAX_LINES",
    "MAX_LINE_BYTES",
    "MAX_TOTAL_TEXT_BYTES",
    "recognize",
)
