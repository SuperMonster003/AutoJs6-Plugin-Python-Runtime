# U1-R2 structured-result and output-artifact protocol

Status: implemented and covered through E2 on the current Host and Plugin
trees. This document does not claim real Binder/CPython device execution,
stable release provenance, publication, or complete U1-R2 acceptance.

## Contract

Protocol 1.4 adds an explicit result channel which is independent of
stdout/stderr. A script may set at most one strict JSON value and may register
bounded files under one Plugin-private execution root. The Host receives the
JSON only from the typed terminal document and receives each file only through
the manifest entry and result PFD with the same descriptor index.

Never infer a result from stdout text. Printed JSON is still only stdout, and
an explicit result remains available even when the script prints unrelated
logs before or after setting it.

The Python surface is deliberately small:

```python
from autojs6 import artifacts, result

report_path = artifacts.path("reports/summary.json")
with open(report_path, "w", encoding="utf-8", newline="\n") as output:
    output.write('{"rows":3}\n')

print("ordinary diagnostic output")
result.set({"ok": True, "rows": 3, "artifact": "reports/summary.json"})
```

`result.set(value)` accepts only JSON-compatible `None`, strings, booleans,
integers, finite floats, lists/tuples, and dictionaries with string keys. It
rejects cycles, nesting deeper than 64, non-finite numbers, unsupported values,
invalid Unicode, a second assignment, and encoded UTF-8 bytes beyond the
negotiated limit. The serialized form is deterministic UTF-8 JSON with sorted
object keys, compact separators, non-ASCII characters preserved, and no NaN or
Infinity extension.

`artifacts.path(relative_path)` registers one NFC-normalized, slash-separated
logical relative path and returns the corresponding writable path inside the
execution-private output root. Absolute paths, drive prefixes, backslashes,
control characters, empty segments, `.` and `..` are rejected. Registering the
same normalized path again is idempotent; distinct paths consume the negotiated
count. Registration alone is not success: after execution, every registered
path must exist as a regular non-symlink file.

If protocol 1.4 result support was not negotiated, these APIs fail with
`CapabilityUnavailableError`. A failed, cancelled, timed-out, output-limited,
or otherwise non-completed execution never publishes a structured result or
artifact.

## Protocol 1.4 extension

The shared API advertises two independent capability bits:

- `supportsStructuredJsonResult`
- `supportsOutputArtifacts`

Their provider limits are `maxStructuredJsonBytes`, `maxOutputArtifacts`,
`maxOutputArtifactPathBytes`, `maxOutputArtifactBytes`, and
`maxTotalOutputArtifactBytes`. Unsupported capabilities must advertise zero
for their associated limits. The current Plugin caps these values at 64 KiB,
16 files, 1024 UTF-8 path bytes, 4 MiB per file, and 8 MiB in aggregate. The
current Host negotiates the smaller defaults of 64 KiB, 8 files, 512 path
bytes, 2 MiB per file, and 4 MiB in aggregate.

The execution request carries a `PythonResultPolicy` in request tag 16. That
tag is required-for-reader, so a 1.3 reader rejects rather than silently
ignoring a result-enabled request. The policy contains all five execution
limits and must enable structured JSON, output artifacts, or both.

The execution result adds:

- optional required-for-reader tag 8: the strict JSON text;
- repeated required-for-reader tag 9: `PythonOutputArtifact` documents.

Each artifact document contains the normalized logical path, a non-negative
result-descriptor index, exact byte length, and a 32-byte SHA-256 digest. Every
result descriptor must be referenced exactly once, every artifact path must be
unique, and count/per-file/aggregate limits are validated against both the
protocol ceiling and the request policy. Unknown older readers therefore fail
closed whenever a provider actually emits a new result field.

The extension uses schema IDs `0x5059001a` (`PythonResultPolicy`) and
`0x5059001b` (`PythonOutputArtifact`). Result admission failures use
`OUTPUT_ARTIFACT_REJECTED` in the `RESULT` phase. The name covers rejection of
either the explicit JSON result or its artifact set; Python exceptions raised
directly by the public API remain ordinary structured Python exceptions.

## Plugin snapshot and Binder ownership

Python writes only to a Plugin-private writable result root. After Python has
returned successfully, the Plugin validates every logical path again, walks
each parent with `lstat`, rejects symlinks and non-regular targets, opens the
file read-only with `O_NOFOLLOW`, and verifies the opened device/inode identity.
It then copies at most the negotiated bytes into a new private snapshot while
computing SHA-256 and checking the aggregate budget. The snapshot is synced,
made read-only, reopened as a read-only `ParcelFileDescriptor`, and described
by the immutable manifest. A writable script file never crosses Binder.

The Host validates the terminal document against the original request policy
before reading a descriptor. It requires each descriptor to be an exact regular
file, reads exactly the declared length, requires immediate EOF, and recomputes
SHA-256. Bytes are then copied into Host-owned immutable values; the public
accessor returns a defensive copy. stdout/stderr remain on the existing ordered
chunk channel and are absent from this result value surface.

The Plugin keeps result descriptors and snapshot roots alive until the terminal
callback is delivered. Callback rejection, callback failure, cancellation,
timeout, service close, and all preparation failures close descriptors and
delete the private roots through a no-follow cleanup walk. Host callback
ownership closes every received descriptor on success or failure.

This containment is a transport guarantee, not a hostile-code sandbox. The
runtime still executes trusted local Python under the Plugin UID; the result
API does not grant a Host `Context`, Binder object, callback sink, or arbitrary
Java object to script globals.

## Compatibility and evidence

Shared tests cover protocol 1.4 capability/request/result round trips,
required-for-reader compatibility failures, validation limits, descriptor
reference exactness, strict JSON grammar, terminal session policy, and SHA-256
goldens. Portable tests cover explicit/canonical JSON, one-assignment and size
failures, result/stdout separation, path/count admission, and unavailable
capabilities. Plugin JVM/build tests cover advertised limits and compilation;
Host targeted tests cover policy selection, request planning, exact reads,
early EOF, trailing bytes, digest mismatch, defensive copies, and the absence
of stdout inference.

Run the current-tree functional gate with:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\verify-u1-r2-structured-results.ps1 `
  -HostRepository D:\idea-projects\AutoJs6
```

Its report is
`build/reports/python/u1/r2-structured-results-contract.json`. A passing report
still has `phaseStatus=PARTIAL`, `r2Complete=false`, `binderExecuted=false`, and
`deviceVerified=false`. U1-R2 becomes complete only after exact Host/Plugin
artifacts pass the separately authorized E3 device transaction. The dedicated
five-selector fixture, exact-device runner, offline verifier and authority
boundary are documented in `U1_R2_DEVICE_EVIDENCE.md`; their presence and an
AndroidTest compile do not claim a device run. A dirty-tree report is
development evidence and cannot establish stable release provenance.
