# Type stub of the AutoJs6 Python Runtime package `autojs6` (mirrors app/src/main/python/autojs6/ocr.py).
# AutoJs6 tools/api-coverage/language_runtimes.py checks its names, signatures and constant values against the plugin.
"""Bounded text recognition through the AutoJs6 Host-selected OCR engine."""

from typing import Final

MAX_LINES: Final = 256
MAX_LINE_BYTES: Final = 4096
MAX_TOTAL_TEXT_BYTES: Final = 49152


def recognize(image: bytes | bytearray | memoryview) -> tuple[str, ...]:
    """Recognize text in one bounded PNG/JPEG image using the configured Host OCR engine."""
    ...
