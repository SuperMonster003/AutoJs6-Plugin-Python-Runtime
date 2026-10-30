# Type stub of the AutoJs6 Python Runtime package `autojs6` (mirrors app/src/main/python/autojs6/images.py).
# AutoJs6 tools/api-coverage/language_runtimes.py checks its names, signatures and constant values against the plugin.
"""Bounded screen capture, color search, and template search through the Host."""

from typing import Final

CHUNK_SCHEMA: Final = "autojs6-python-screen-image-chunk-v1"
COLOR_MATCH_SCHEMA: Final = "autojs6-python-color-match-v1"
IMAGE_MATCH_SCHEMA: Final = "autojs6-python-image-match-v1"
IMAGE_SCHEMA: Final = "autojs6-python-screen-image-v1"
MAX_CHUNKS: Final = 128
MAX_CHUNK_BYTES: Final = 32768
MAX_COLOR: Final = 16777215
MAX_COLOR_THRESHOLD: Final = 255
MAX_DIMENSION: Final = 8192
MAX_IMAGE_BYTES: Final = 4194304
MAX_PIXELS: Final = 16777216
MAX_QUALITY: Final = 100
MIN_QUALITY: Final = 1
MAX_TEMPLATE_BYTES: Final = 1048576
MAX_TEMPLATE_CHUNK_BYTES: Final = 24576
MAX_TEMPLATE_CHUNKS: Final = 43
MAX_TEMPLATE_DIMENSION: Final = 2048
MAX_TEMPLATE_PIXELS: Final = 1048576
TEMPLATE_CHUNK_SCHEMA: Final = "autojs6-python-image-template-chunk-v1"
TEMPLATE_SCHEMA: Final = "autojs6-python-image-template-v1"


def capture_screen(*, format: str = ..., quality: int = ..., path: str | None = ...) -> bytes | str:
    """Capture the current screen as bytes or atomically write one output artifact."""
    ...


def find_color(
    color: int | str,
    *,
    region: tuple[int, int, int, int] | list[int] | None = ...,
    threshold: int = ...,
) -> tuple[int, int] | None:
    """Return the first row-major screen coordinate matching one RGB color."""
    ...


def find_image(
    template: bytes | bytearray | memoryview,
    *,
    region: tuple[int, int, int, int] | list[int] | None = ...,
    threshold: int = ...,
) -> tuple[int, int] | None:
    """Return the first row-major coordinate matching one bounded PNG/JPEG template."""
    ...
