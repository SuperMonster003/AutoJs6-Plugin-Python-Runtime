# Host OCR recognition

`autojs6.ocr` exposes one bounded text-recognition operation backed by the OCR
engine which AutoJs6 has already enabled, authorized, and selected. The Python
Runtime Plugin does not package an OCR model, select an untrusted service, or
fall back to a different implementation.

```python
from autojs6 import ocr

lines = ocr.recognize(image)
```

`image` must be PNG or JPEG `bytes`, `bytearray`, or a byte-oriented
`memoryview`. The result is an immutable `tuple[str, ...]` in the exact order
returned by the selected Host OCR plugin. Empty recognition is `()`; the facade
does not merge, trim, sort, deduplicate, or otherwise reinterpret lines.

## Engine selection

The Host discovers OCR services through its existing compatibility action
`org.autojs.plugin.PADDLE_OCR`. It considers only services which are enabled in
the plugin center, authorized by the Host trust manager, and compatible with
the current Host version. Existing engine/variant priority settings choose
among eligible services. This alpha API intentionally has no engine, language,
profile, threshold, or raw-image option: it follows the same configured Host
default that an option-free AutoJs6 OCR call would use.

Recognition itself does not require the AutoJs6 accessibility service. The
input may come from a project file, another trusted source, or a prior
`images.capture_screen()` call. A captured image must still fit the smaller OCR
upload envelope described below.

## Image transfer and lifetime

OCR reuses the execution-local bounded image-template transport; it does not
add another arbitrary byte channel:

- encoded size is 1 byte through 1 MiB;
- the format is inferred from an exact PNG signature or JPEG start/end marker;
- Python declares the length and SHA-256, then sends canonical Base64 in ordered
  raw chunks of at most 24 KiB (at most 43 chunks);
- Android decode is limited to 2048 pixels per side and 1,048,576 pixels total;
- because the shared retained-image representation also serves template
  matching, at least one decoded pixel must have alpha exactly 255. Ordinary
  screenshots and JPEG files satisfy this condition;
- the Host owns at most one pending or decoded upload for the execution. A new
  upload replaces and clears the prior one.

After upload, the Host copies the retained pixels into a temporary
`ARGB_8888` bitmap, clears the copied integer array, and delegates that bitmap
to `OcrPluginHost`. The existing OCR transport sends an image file descriptor
to the selected external OCR service. The temporary bitmap is erased and
recycled in `finally`. Python always calls `images.release_template` for every
usable image ID and overwrites its mutable upload copy; Host replacement,
release, decode failure, and broker terminal clear retained encoded/pixel
arrays.

One recognition therefore consumes one begin call, 1-43 upload calls, one OCR
call, and one release call from the protocol 1.5 execution quota of 1024 calls.
Each broker request and response remains limited to 64 KiB.

## Result bounds

The Host validates the external engine result before encoding it, and Python
repeats the same checks after decoding:

| Limit | Value |
| --- | ---: |
| Recognized lines | 256 |
| One line | 4 KiB strict UTF-8 |
| Aggregate line text | 48 KiB strict UTF-8 |
| Broker response | 64 KiB encoded JSON |

The aggregate limit counts the UTF-8 bytes in the returned lines. JSON escaping
still has to fit the independent 64 KiB response limit, so control-heavy text
may reach that outer limit first. Invalid Unicode, non-text entries, or any
malformed response is rejected rather than silently repaired.

## Errors

- Invalid local types raise `TypeError`; empty, oversized, malformed, or
  unsupported encoded images raise `ValueError` before an OCR call.
- Corrupt Android decode results, SHA-256 mismatch, impossible dimensions, or
  an image with no fully opaque pixel use `HostCapabilityError` code
  `INVALID_IMAGE_TEMPLATE`.
- Encoded, decoded, result-count, line, aggregate, or response overflow uses
  `RESULT_LIMIT_EXCEEDED`.
- An unknown, replaced, released, or terminal upload uses `STALE_TEMPLATE`.
- If no enabled, authorized, compatible OCR service can be selected, the Host
  returns `OCR_UNAVAILABLE`, which the Python broker maps to
  `CapabilityUnavailableError`.
- A selected service which fails during recognition returns
  `HostCapabilityError` with stable code `OCR_FAILED`; internal exception text
  is not exposed to Python.
- A malformed Host result is rejected as `BROKER_PROTOCOL_ERROR`.

Cleanup never replaces a primary upload/recognition/protocol exception with a
secondary release exception. If recognition succeeds, however, a release
failure remains visible instead of being silently ignored.

## Timeout and cancellation boundary

OCR selection, binding, and image handoff use AutoJs6's existing OCR plugin
host and its 60-second admission/call budget. The external recognition AIDL
method is synchronous, so this alpha does not claim hard per-inference
preemption once a third-party engine is inside that Binder call. The configured
overall Python execution deadline still applies, and explicit cancellation
uses the Runtime's authoritative process-restart terminal mode.

## Focused current-tree validation

The public Python project-engine path was exercised against Host 5276 and
Plugin `0.4.0-alpha.6`/66 on 2026-08-24. An API 37 x86_64 16 KiB-page emulator
used an installed, SM003-signed ML Kit OCR `1.0.0`/4 service to recognize an
instrumentation-generated 1200 x 320 PNG containing `AUTOJS6 OCR 2026`.
Python returned a tuple whose combined text contained all three controlled
tokens, published no artifact, and reported `OK (1 test)` in 2.873 seconds.
Accessibility remained disabled with a null service list before and after.

On Sony XQ-AT72 (`QV710AF65F`, API 31, arm64-v8a, 4 KiB pages), no OCR service
was installed. The same public API returned `CapabilityUnavailableError` with
the exact bounded unavailable message and reported `OK (1 test)` in 0.918
seconds. Its pre-existing six-service accessibility list was byte-for-byte
unchanged. Both runs used replacement installs without uninstalling packages
or clearing application data. This is focused current-tree acceptance, not a
published release or a complete device matrix.

## Deliberate limits

Only line-oriented `recognizeText` is exposed. Detection boxes, confidence,
orientation, language/profile selection, engine selection, mutable image
objects, preprocessing, and capture-to-OCR Host handles remain undeclared. The
API never installs, enables, authorizes, downloads, or opens settings for an OCR
plugin.

See [`m3_ocr.py`](../../examples/python/m3_ocr.py) for a minimal project-local
example, [`HOST_IMAGES.md`](HOST_IMAGES.md) for the shared upload envelope, and
[`PYTHON_SEMANTICS_CONTRACT.md`](PYTHON_SEMANTICS_CONTRACT.md) for normative
execution and broker semantics.
