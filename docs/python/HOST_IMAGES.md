# Host screen images and color search

`autojs6.images` exposes bounded screen capture and one-shot RGB color search
through the AutoJs6 Host accessibility service. Capture transfers only validated
PNG or JPEG bytes. Color search remains entirely in the Host and returns only a
coordinate or a deterministic miss. Android `Bitmap`, `HardwareBuffer`,
accessibility-service, callback, and Binder objects never cross into the Python
process.

## Prerequisite

Screen capture requires Android 11 (API 30) or newer and an enabled, connected,
operational AutoJs6 accessibility service. The API never enables that service,
opens Android settings, starts MediaProjection, or shows a screen-sharing
permission prompt. Unsupported Android versions and unavailable accessibility
fail closed with `CapabilityUnavailableError` before a capture is attempted.

## Public API

```python
from autojs6 import images

images.capture_screen(
    *,
    format: str = "png",
    quality: int = 100,
    path: str | None = None,
) -> bytes | str

images.find_color(
    color: int | str,
    *,
    region: tuple[int, int, int, int] | list[int] | None = None,
    threshold: int = 0,
) -> tuple[int, int] | None
```

`format` accepts exactly `"png"` or `"jpeg"`. `quality` is a strict non-boolean
integer from 1 through 100. Android ignores the quality setting for lossless PNG
encoding; it controls JPEG compression.

With the default `path=None`, the function returns immutable encoded `bytes`.
With a normalized execution-relative artifact path, it atomically writes the
verified image into the Plugin-private output area and returns that private
absolute path. The logical path is published in the ordinary execution result;
the Host never receives a writable Plugin path.

```python
from autojs6 import images, result

private_path = images.capture_screen(path="screens/current.png")
result.set({"artifact": "screens/current.png", "privatePath": private_path})
```

## Color search

`find_color` accepts a strict non-boolean integer from `0x000000` through
`0xFFFFFF`, or text in the exact `#RRGGBB` form. Alpha is neither accepted nor
compared. `threshold` is a strict integer from 0 through 255 and applies
independently to the absolute red, green, and blue channel differences.

The optional region is a tuple or list `(x, y, width, height)`. Origins range
from 0 through 8191, sizes from 1 through 8192, and each origin plus size must
remain within the fixed 8192-pixel contract. The Host repeats these checks and
also proves that the region fits the fresh screenshot.

Each call takes a new Android 11+ accessibility screenshot and scans only the
requested region from top to bottom, then left to right. It returns the first
matching absolute screen coordinate as `(x, y)`, or `None` after an exhaustive
miss. Search ignores the Android pixel alpha channel. The strict response schema
is `autojs6-python-color-match-v1`; Python verifies exact fields, flag/coordinate
consistency, fixed coordinate bounds, and requested-region containment.

```python
from autojs6 import images, result

match = images.find_color("#123456", region=(0, 200, 1080, 1200), threshold=2)
result.set({"match": None if match is None else list(match)})
```

No encoded image, pixel row, Android image object, or retained image handle is
sent to or kept by the Plugin for color search. The Host allocates one bounded
row buffer, clears it before return, and recycles the fresh screenshot in
`finally`. A color search neither consumes nor replaces the encoded image slot
used by `capture_screen`.

## Capture transfer and resource bounds

- The Host retains at most one encoded screenshot for the current execution.
  A replacement, explicit release, or execution terminal clears and zeroes the
  retained byte array.
- Width and height are each capped at 8192 pixels, total area at 16,777,216
  pixels, and encoded data at 4 MiB.
- Python downloads the image in ordered raw chunks of at most 32 KiB. At most
  128 chunks can be accepted for one capture.
- The descriptor and every chunk use exact protocol schemas. Python verifies
  the opaque image ID, format, dimensions, area, byte length, contiguous
  offsets, canonical Base64, full non-final chunks, EOF position, SHA-256, and
  PNG/JPEG signatures before returning or writing anything.
- A valid Host image ID is released in `finally` after a malformed descriptor,
  bad chunk, cancellation-visible broker failure, digest mismatch, or successful
  transfer. Release completes before returned bytes are exposed or an artifact
  write begins. A release failure is reported when transfer otherwise succeeded,
  but never masks the primary transfer failure.
- Python assembles the result in a mutable buffer and overwrites that buffer
  after copying the returned bytes, after writing the artifact, or on failure.

The normal protocol 1.5 limits of 1024 Host calls, 64 KiB per request/response,
and 5 seconds per individual Host action still apply. Host capture itself has a
single bounded four-second deadline; it does not loop indefinitely. A complete
color search is one broker call and does not transfer screenshot bytes.

## Errors

- Invalid local argument types raise `TypeError`; unsupported formats, malformed
  colors/regions, or out-of-range quality, coordinates, sizes, and thresholds
  raise `ValueError` without a Host call.
- Android/API or accessibility absence uses `CapabilityUnavailableError` with
  stable Host codes `SCREEN_CAPTURE_UNAVAILABLE` or
  `ACCESSIBILITY_UNAVAILABLE`.
- Platform capture, search, or encoding failure uses `HostCapabilityError` with
  `SCREEN_CAPTURE_FAILED`.
- Image-size boundaries use `RESULT_LIMIT_EXCEEDED`; an unknown, replaced,
  released, or terminal image reference uses `STALE_IMAGE`.
- Any malformed descriptor, chunk, or color-match result is rejected as
  `BROKER_PROTOCOL_ERROR`.

## Deliberate limits

The module currently returns encoded bytes or an output artifact, not a mutable
image object. It does not expose cropping, rotation, arbitrary pixel access,
`find_image`, template upload, OCR, MediaProjection capture, or background
service enablement. Those are separate Roadmap slices and are not implied by
`capture_screen` or `find_color`.

See [`m3_capture_screen.py`](../../examples/python/m3_capture_screen.py) and
[`m3_find_color.py`](../../examples/python/m3_find_color.py) for minimal
examples, [`HOST_AUTOMATOR.md`](HOST_AUTOMATOR.md) and
[`HOST_SELECTOR.md`](HOST_SELECTOR.md) for actions/UI data, and
[`PYTHON_SEMANTICS_CONTRACT.md`](PYTHON_SEMANTICS_CONTRACT.md) for normative
execution and broker semantics.
