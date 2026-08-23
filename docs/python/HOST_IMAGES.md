# Host screen images, color search, and template search

`autojs6.images` exposes bounded screen capture, one-shot RGB color search, and
one-shot PNG/JPEG template search through the AutoJs6 Host accessibility
service. Capture transfers only validated PNG or JPEG bytes. Color search stays
entirely in the Host. Template search uploads one bounded encoded template but
keeps every screenshot and all decoded pixels in the Host. Android `Bitmap`,
`HardwareBuffer`, accessibility-service, callback, and Binder objects never
cross into the Python process.

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

images.find_image(
    template: bytes | bytearray | memoryview,
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

## Template search

`find_image` accepts encoded PNG or JPEG data as `bytes`, `bytearray`, or a
byte-oriented `memoryview`. It does not accept a filesystem path or an Android
image object; ordinary project code can use `Path(...).read_bytes()` explicitly.
Python recognizes the exact PNG/JPEG signature, copies the data into a mutable
temporary buffer, verifies every upload response, and overwrites that buffer in
`finally`.

The optional region and `threshold` have the same shape and strict non-boolean
integer rules as `find_color`. A hit is the absolute screen coordinate of the
template's top-left corner. Candidates are considered top-to-bottom and then
left-to-right, so the first result is deterministic. Exhaustive absence returns
`None`.

```python
from pathlib import Path

from autojs6 import images, result

template = Path("fixtures/target.png").read_bytes()
match = images.find_image(template, region=(0, 200, 1080, 1200), threshold=2)
result.set({"match": None if match is None else list(match)})
```

The Host compares absolute red, green, and blue channel differences against the
per-channel threshold. Only template pixels whose decoded alpha is exactly 255
participate. Every other template pixel is a wildcard, and a template must have
at least one fully opaque pixel. JPEG templates are fully opaque after decode.
This alpha rule is deliberate and fixed; semi-transparent pixels are not
blended against screenshot pixels.

One execution retains at most one pending upload or decoded template. Beginning
a replacement, explicit release, any upload/decode failure, or execution
terminal clears the encoded upload and decoded pixel/offset buffers. Python
releases every usable template ID in `finally`. A release failure is exposed
when the search otherwise succeeded, but never masks the primary upload,
capture, search, or protocol failure.

Template transfer and matching are bounded as follows:

- encoded PNG/JPEG data is 1 byte through 1 MiB;
- raw upload chunks are ordered, contiguous, canonical Base64 representations
  of at most 24 KiB, with every non-final chunk exactly 24 KiB;
- the Host verifies the declared byte length and SHA-256 before decode;
- decoded width and height are each at most 2048, and decoded area is at most
  1,048,576 pixels;
- the requested screenshot region is at most 4,194,304 pixels;
- one search performs at most 16,777,216 bounded pixel comparisons, including
  anchor prechecks; exceeding the budget fails rather than returning a false
  miss.

The Host decodes with Android `BitmapFactory`, uses a small deterministic set of
opaque anchor pixels only as a rejection optimization, and then verifies every
opaque pixel before reporting a hit. It does not require, load, or fall back to
the AutoJs6 OpenCV plugin. The strict pure-data schemas are
`autojs6-python-image-template-v1`,
`autojs6-python-image-template-chunk-v1`, and
`autojs6-python-image-match-v1`.

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
- Template upload is independent of the retained encoded screenshot slot. It
  uses one execution-local template slot, ordered 24 KiB raw chunks, a 1 MiB
  encoded cap, SHA-256 verification, bounded Android decode, and explicit
  release as described above.

The normal protocol 1.5 limits of 1024 Host calls, 64 KiB per request/response,
and 5 seconds per individual Host action still apply. Host capture itself has a
single bounded four-second deadline; it does not loop indefinitely. A complete
color search is one broker call and does not transfer screenshot bytes. Template
search additionally uses one begin call, one through 43 upload calls, one search
call, and one release call.

Android rejects accessibility screenshot requests made within 333 ms of the
previous accepted request. When, and only when, the platform returns
`ERROR_TAKE_SCREENSHOT_INTERVAL_TIME_SHORT`, the Host waits 350 ms and retries
within the same four-second deadline, for at most three total attempts. Other
platform failures, interruption, deadline exhaustion, and unavailable services
still fail closed immediately. This bounded policy makes consecutive
`find_color`, `find_image`, and `capture_screen` calls deterministic without an
unbounded polling loop.

## Errors

- Invalid local argument types raise `TypeError`; unsupported formats, malformed
  image signatures/colors/regions, oversized templates, or out-of-range
  quality, coordinates, sizes, and thresholds raise `ValueError` without a Host
  call.
- Android/API or accessibility absence uses `CapabilityUnavailableError` with
  stable Host codes `SCREEN_CAPTURE_UNAVAILABLE` or
  `ACCESSIBILITY_UNAVAILABLE`.
- Platform capture, search, or encoding failure uses `HostCapabilityError` with
  `SCREEN_CAPTURE_FAILED`.
- Image/template/region/comparison boundaries use `RESULT_LIMIT_EXCEEDED`; an
  unknown, replaced, released, or terminal encoded-image reference uses
  `STALE_IMAGE`, while the equivalent template condition uses `STALE_TEMPLATE`.
- Invalid signatures, corrupt or unsupported Android decode results, dimension
  inconsistencies, SHA-256 mismatch, or an all-wildcard template use
  `INVALID_IMAGE_TEMPLATE`.
- Any malformed descriptor, chunk acknowledgement, color match, or template
  match result is rejected as `BROKER_PROTOCOL_ERROR`.

## Deliberate limits

The module currently returns encoded bytes or an output artifact, not a mutable
image object. It does not expose cropping, rotation, arbitrary pixel access,
template creation from a retained capture, multi-scale/rotated matching, OCR,
MediaProjection capture, or background service enablement. Those are separate
Roadmap slices and are not implied by the current exact-size RGB matcher.

See [`m3_capture_screen.py`](../../examples/python/m3_capture_screen.py),
[`m3_find_color.py`](../../examples/python/m3_find_color.py), and
[`m3_find_image.py`](../../examples/python/m3_find_image.py) for minimal
examples, [`HOST_AUTOMATOR.md`](HOST_AUTOMATOR.md) and
[`HOST_SELECTOR.md`](HOST_SELECTOR.md) for actions/UI data, and
[`PYTHON_SEMANTICS_CONTRACT.md`](PYTHON_SEMANTICS_CONTRACT.md) for normative
execution and broker semantics.
