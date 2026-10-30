# Type stub of the AutoJs6 Python Runtime package `autojs6` (mirrors app/src/main/python/autojs6/images.py).
# AutoJs6 tools/api-coverage/language_runtimes.py checks its names and signatures against the plugin.
"""Bounded screen capture, color search, and template search through the Host."""

from typing import Final

CHUNK_SCHEMA: Final[str]
COLOR_MATCH_SCHEMA: Final[str]
IMAGE_MATCH_SCHEMA: Final[str]
IMAGE_SCHEMA: Final[str]
MAX_CHUNKS: Final[int]
MAX_CHUNK_BYTES: Final[int]
MAX_COLOR: Final[int]
MAX_COLOR_THRESHOLD: Final[int]
MAX_DIMENSION: Final[int]
MAX_IMAGE_BYTES: Final[int]
MAX_PIXELS: Final[int]
MAX_QUALITY: Final[int]
MIN_QUALITY: Final[int]
MAX_TEMPLATE_BYTES: Final[int]
MAX_TEMPLATE_CHUNK_BYTES: Final[int]
MAX_TEMPLATE_CHUNKS: Final[int]
MAX_TEMPLATE_DIMENSION: Final[int]
MAX_TEMPLATE_PIXELS: Final[int]
TEMPLATE_CHUNK_SCHEMA: Final[str]
TEMPLATE_SCHEMA: Final[str]


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
