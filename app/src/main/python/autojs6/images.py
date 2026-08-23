"""Bounded execution-local screen capture through Host accessibility."""

from __future__ import annotations

import base64
import binascii
import hashlib
import os
import re
import sys
import tempfile
from typing import Any, NoReturn

from . import artifacts as _artifacts
from ._broker import _call, _expect_none, _expect_object, _protocol_error


IMAGE_SCHEMA = "autojs6-python-screen-image-v1"
CHUNK_SCHEMA = "autojs6-python-screen-image-chunk-v1"
MAX_IMAGE_BYTES = 4 * 1024 * 1024
MAX_CHUNK_BYTES = 32 * 1024
MAX_CHUNKS = MAX_IMAGE_BYTES // MAX_CHUNK_BYTES
MAX_DIMENSION = 8_192
MAX_PIXELS = 16 * 1024 * 1024
MIN_QUALITY = 1
MAX_QUALITY = 100

_FORMATS = frozenset(("png", "jpeg"))
_IMAGE_ID = re.compile(r"image-[1-9][0-9]*")
_SHA256 = re.compile(r"[0-9a-f]{64}")
_DESCRIPTOR_KEYS = frozenset(
    ("schema", "id", "format", "width", "height", "byteLength", "sha256")
)
_CHUNK_KEYS = frozenset(
    ("schema", "imageId", "offset", "data", "nextOffset", "eof")
)
_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
_JPEG_START = b"\xff\xd8"
_JPEG_END = b"\xff\xd9"


def capture_screen(
    *,
    format: str = "png",
    quality: int = 100,
    path: str | None = None,
) -> bytes | str:
    """Capture the current screen as bytes or atomically write one output artifact."""
    image_format = _format(format)
    image_quality = _integer(quality, "Screen capture quality", MIN_QUALITY, MAX_QUALITY)
    if path is not None and type(path) is not str:
        raise TypeError("Screen capture artifact path must be text or None")

    payload = _download(image_format, image_quality)
    try:
        if path is None:
            return bytes(payload)
        target = _artifacts.path(path)
        _write_atomic(target, payload)
        return target
    finally:
        _zero(payload)


def _download(image_format: str, image_quality: int) -> bytearray:
    payload = bytearray()
    release_id: str | None = None
    try:
        try:
            raw_descriptor = _expect_object(
                _call(
                    "images.capture_screen",
                    {"format": image_format, "quality": image_quality},
                ),
                "images.capture_screen",
            )
            release_id = _release_candidate(raw_descriptor.get("id"))
            image_id, byte_length, expected_sha256 = _descriptor(
                raw_descriptor,
                image_format,
            )
            release_id = image_id

            offset = 0
            for _ in range(MAX_CHUNKS):
                raw_chunk = _expect_object(
                    _call(
                        "images.read_chunk",
                        {"imageId": image_id, "offset": offset},
                    ),
                    "images.read_chunk",
                )
                chunk, next_offset, eof = _chunk(
                    raw_chunk,
                    image_id=image_id,
                    expected_offset=offset,
                    byte_length=byte_length,
                )
                payload.extend(chunk)
                offset = next_offset
                if eof:
                    break
            else:
                _invalid("images.read_chunk exceeded the fixed chunk count")

            if len(payload) != byte_length:
                _invalid("images.read_chunk returned an incomplete image")
            if hashlib.sha256(payload).hexdigest() != expected_sha256:
                _invalid("images.read_chunk returned an image with a mismatched SHA-256")
            _validate_signature(payload, image_format)
        finally:
            if release_id is not None:
                if sys.exc_info()[0] is None:
                    _release(release_id)
                else:
                    try:
                        _release(release_id)
                    except BaseException:
                        pass
    except BaseException:
        _zero(payload)
        raise
    return payload


def _descriptor(
    value: dict[str, Any],
    requested_format: str,
) -> tuple[str, int, str]:
    if set(value) != _DESCRIPTOR_KEYS:
        _invalid("images.capture_screen returned invalid fields")
    if value["schema"] != IMAGE_SCHEMA:
        _invalid("images.capture_screen returned an invalid schema")
    image_id = value["id"]
    if _release_candidate(image_id) is None:
        _invalid("images.capture_screen returned an invalid image ID")
    if value["format"] != requested_format:
        _invalid("images.capture_screen returned an unexpected image format")
    width = _response_integer(value["width"], "width", 1, MAX_DIMENSION)
    height = _response_integer(value["height"], "height", 1, MAX_DIMENSION)
    if width * height > MAX_PIXELS:
        _invalid("images.capture_screen returned too many pixels")
    byte_length = _response_integer(
        value["byteLength"],
        "byte length",
        1,
        MAX_IMAGE_BYTES,
    )
    sha256 = value["sha256"]
    if type(sha256) is not str or _SHA256.fullmatch(sha256) is None:
        _invalid("images.capture_screen returned an invalid SHA-256")
    return image_id, byte_length, sha256


def _chunk(
    value: dict[str, Any],
    *,
    image_id: str,
    expected_offset: int,
    byte_length: int,
) -> tuple[bytes, int, bool]:
    if set(value) != _CHUNK_KEYS:
        _invalid("images.read_chunk returned invalid fields")
    if value["schema"] != CHUNK_SCHEMA:
        _invalid("images.read_chunk returned an invalid schema")
    if value["imageId"] != image_id:
        _invalid("images.read_chunk returned the wrong image ID")
    if type(value["offset"]) is not int or value["offset"] != expected_offset:
        _invalid("images.read_chunk returned a non-contiguous offset")

    encoded = value["data"]
    if type(encoded) is not str:
        _invalid("images.read_chunk returned non-text Base64 data")
    try:
        decoded = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as error:
        raise _protocol_error("images.read_chunk returned invalid Base64 data", error)
    if base64.b64encode(decoded).decode("ascii") != encoded:
        _invalid("images.read_chunk returned non-canonical Base64 data")
    if not 1 <= len(decoded) <= MAX_CHUNK_BYTES:
        _invalid("images.read_chunk returned an invalid chunk size")

    next_offset = value["nextOffset"]
    if type(next_offset) is not int or next_offset != expected_offset + len(decoded):
        _invalid("images.read_chunk returned an invalid next offset")
    if next_offset > byte_length:
        _invalid("images.read_chunk exceeded the declared byte length")
    eof = value["eof"]
    if type(eof) is not bool or eof != (next_offset == byte_length):
        _invalid("images.read_chunk returned an invalid EOF state")
    if not eof and len(decoded) != MAX_CHUNK_BYTES:
        _invalid("images.read_chunk returned a short non-final chunk")
    return decoded, next_offset, eof


def _release(image_id: str) -> None:
    _expect_none(
        _call("images.release", {"imageId": image_id}),
        "images.release",
    )


def _release_candidate(value: Any) -> str | None:
    if type(value) is not str or len(value) > 64 or _IMAGE_ID.fullmatch(value) is None:
        return None
    return value


def _format(value: Any) -> str:
    if type(value) is not str:
        raise TypeError("Screen capture format must be text")
    if value not in _FORMATS:
        raise ValueError("Screen capture format must be 'png' or 'jpeg'")
    return value


def _integer(value: Any, label: str, minimum: int, maximum: int) -> int:
    if type(value) is not int:
        raise TypeError(f"{label} must be an integer")
    if not minimum <= value <= maximum:
        raise ValueError(f"{label} must be between {minimum} and {maximum}")
    return value


def _response_integer(value: Any, label: str, minimum: int, maximum: int) -> int:
    if type(value) is not int or not minimum <= value <= maximum:
        _invalid(f"images.capture_screen returned an invalid {label}")
    return value


def _validate_signature(payload: bytearray, image_format: str) -> None:
    if image_format == "png":
        valid = payload.startswith(_PNG_SIGNATURE)
    else:
        valid = payload.startswith(_JPEG_START) and payload.endswith(_JPEG_END)
    if not valid:
        _invalid("images.capture_screen returned bytes with an invalid format signature")


def _write_atomic(target: str, payload: bytearray) -> None:
    parent = os.path.dirname(target)
    descriptor, temporary = tempfile.mkstemp(prefix=".autojs6-capture-", dir=parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            descriptor = -1
            written = stream.write(payload)
            if written != len(payload):
                raise OSError("Screen capture artifact write was incomplete")
        os.replace(temporary, target)
        temporary = ""
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if temporary:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass


def _zero(payload: bytearray) -> None:
    if payload:
        payload[:] = b"\0" * len(payload)


def _invalid(message: str) -> NoReturn:
    raise _protocol_error(message)


__all__ = (
    "CHUNK_SCHEMA",
    "IMAGE_SCHEMA",
    "MAX_CHUNKS",
    "MAX_CHUNK_BYTES",
    "MAX_DIMENSION",
    "MAX_IMAGE_BYTES",
    "MAX_PIXELS",
    "MAX_QUALITY",
    "MIN_QUALITY",
    "capture_screen",
)
