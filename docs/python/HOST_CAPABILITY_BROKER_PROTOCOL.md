# Python Host Capability Broker Protocol 1.5

Status: implemented in the current Host and Plugin development trees. The first
capability slice covers toast, clipboard, application launch/navigation, live
device state, level-aware Host console output and permission-aware notices. The
second slice now includes bounded execution-relative Host files,
foreground-only alert, confirmation, text-prompt and selection dialogs, and
bounded current-engine/self-stop/non-Python child-launch operations. All three
second-slice portions passed one API 31 arm64 physical-device smoke and one API
37 x86_64 16 KiB-page emulator smoke on 2026-08-23. This document describes the
reusable broker contract; it does not claim that later Roadmap capabilities, a
complete device matrix or a published release exist.

## Negotiation and Binder compatibility

Provider metadata advertises protocol range `1.0-1.5` and
`supportsHostCapabilityBroker=true`. A Host may select the live broker only
when the negotiated protocol is at least 1.5 and the Provider advertises that
flag.

`IPythonRuntimeProvider.openSession` retains its historical AIDL order and is
used for protocol 1.0 through 1.4. Protocol 1.5 appends
`openSessionWithHostCapabilities(request, descriptors, broker,
admissionCallback, executionCallback)`. The Provider rejects a 1.5 request
without exactly one live broker and rejects a pre-1.5 request which attempts to
supply one. This preserves existing Binder transaction numbers and prevents a
new request from silently running without its live capability channel.

The Host-generated `python-runtime-api.aar` is the authority for the AIDL and
tagged metadata model. The Plugin locks the exact AAR SHA-256 and the clean Host
distribution manifest in `locks/host-api-aars.lock`.

## Execution binding and lifecycle

There is one broker per admitted execution:

1. The Host constructs the broker with the execution request UUID, the exact
   plugin UID pinned during provider discovery, and the enabled capability set.
2. The Host opens the session through the protocol 1.5 AIDL method.
3. The Plugin links the broker Binder to the same death handling used by its
   admission and execution callbacks, then gives the bootstrap one private
   `dispatch(String) -> String` bridge.
4. The bootstrap installs an execution-local Python client immediately before
   user code and removes it in `finally` while restoring all other interpreter
   state.
5. Host terminal, cancellation, callback loss, setup failure or client cleanup
   closes the Host dispatcher. Plugin terminal, cancellation, broker death or
   service/session cleanup closes the private bridge.
6. Calls admitted before cancellation may have performed their Host side
   effect, but are never replayed. Calls after close fail with
   `CapabilityUnavailableError` or a stable closed-broker response.

The Python client serializes an entire request/response exchange with one
execution-local lock. Call IDs therefore increase from 1 without duplicates,
and cleanup waits for an in-flight exchange before revoking copied
`contextvars` contexts.

## Strict JSON wire format

Both directions are non-empty strict UTF-8 JSON objects. The Python client emits
canonical requests with unique fields and rejects duplicate response fields.
Malformed values, missing fields, extra fields and mismatched execution/call IDs
are rejected at the receiving boundary.

Request:

```json
{
  "arguments": {"text": "hello"},
  "callId": 1,
  "capability": "toast.show",
  "executionId": "12345678-1234-5678-9abc-def012345678",
  "version": 1
}
```

Success:

```json
{
  "callId": 1,
  "executionId": "12345678-1234-5678-9abc-def012345678",
  "ok": true,
  "value": null,
  "version": 1
}
```

Failure:

```json
{
  "callId": 1,
  "error": {"code": "INVALID_ARGUMENT", "message": "Host capability arguments are invalid"},
  "executionId": "12345678-1234-5678-9abc-def012345678",
  "ok": false,
  "version": 1
}
```

The JSON document version is independent of the outer Python runtime protocol
version. Capability names use lowercase dotted identifiers. Arguments are an
exact object defined by the selected capability.

## Limits

| Limit | Value |
| --- | ---: |
| Calls admitted per execution | 1024 |
| Encoded request | 64 KiB |
| Encoded response | 64 KiB |
| One text argument | 32 KiB UTF-8 |
| One notice text argument | 4 KiB UTF-8, non-empty |
| One Host file path | 4 KiB UTF-8, normalized relative path |
| One Host text file read/write | 32 KiB UTF-8 |
| One direct directory listing | 128 names, each at most 255 UTF-8 bytes |
| One dialog title | 256 UTF-8 bytes, non-empty |
| One dialog content | 4 KiB UTF-8 |
| One prompt default or reply | 32 KiB UTF-8 |
| One selection list | 1-64 non-empty items, each at most 1 KiB and at most 32 KiB total |
| Successful asynchronous child-script launches per execution | 16 |
| One engine name / source name | 256 / 1024 UTF-8 bytes |
| One ordinary Host main-thread action wait | 5 s |
| One foreground dialog response wait | 5 min |

The overall Python execution deadline still applies independently. A dialog
call holds one broker call until the user responds, the dialog is dismissed,
the execution is cancelled, or its five-minute dialog wait expires. Exhausting
the call quota does not extend either deadline.

## Stable errors

The Host dispatcher can return:

| Code | Meaning |
| --- | --- |
| `CAPABILITY_UNAVAILABLE` | The method is unknown or was not granted |
| `INVALID_ARGUMENT` | Exact argument fields, text/path bounds, package name or URL shape failed |
| `HOST_FAILURE` | The Host action or file I/O failed without exposing internal details |
| `HOST_TIMEOUT` | Dispatch to the Host main thread exceeded 5 seconds |
| `PERMISSION_DENIED` | Notification or Host filesystem permission denied the operation |
| `BROKER_CLOSED` | The execution-scoped dispatcher is already closed |
| `REPLAYED_CALL` | A positive call ID was reused |
| `CALL_LIMIT_EXCEEDED` | The execution consumed all 1024 calls |
| `RESULT_LIMIT_EXCEEDED` | The encoded result or a file/list-specific result limit was exceeded |
| `PATH_NOT_FOUND` | The requested Host file or required parent directory does not exist |
| `PATH_TYPE_MISMATCH` | A file operation received a directory or vice versa |
| `FILE_ENCODING_ERROR` | A Host file is not strict UTF-8 text |
| `INTERACTIVE_NOT_ALLOWED` | A Host dialog was requested without a live foreground Activity-backed grant |
| `NESTED_PYTHON_NOT_ALLOWED` | `engines.run` selected Python while the provider's one active session is occupied |
| `ENGINE_LAUNCH_LIMIT_EXCEEDED` | The execution already launched 16 child Host scripts successfully |

`CAPABILITY_UNAVAILABLE` and `BROKER_CLOSED` become
`autojs6.CapabilityUnavailableError`. Other Host failures become
`autojs6.HostCapabilityError`; its public `code` attribute contains the stable
code. A dead Binder, closed private bridge or missing negotiated broker becomes
`CapabilityUnavailableError`. A malformed/mismatched response becomes
`HostCapabilityError` with code `BROKER_PROTOCOL_ERROR`.

## Current Python facade

| Python API | Capability | Arguments | Result |
| --- | --- | --- | --- |
| `autojs6.toast(text: str) -> None` | `toast.show` | `{"text": text}` | `null` |
| `autojs6.clip.get() -> str` | `clip.get` | `{}` | clipboard text or `""` |
| `autojs6.clip.set(text: str) -> None` | `clip.set` | `{"text": text}` | `null` |
| `autojs6.app.launch(package_name: str) -> bool` | `app.launch` | `{"package": package_name}` | whether an activity launched |
| `autojs6.app.launch_app(name: str) -> bool` | `app.launch_app` | `{"name": name}` | whether an application label resolved and launched |
| `autojs6.app.open_url(url: str) -> bool` | `app.open_url` | `{"url": url}` | whether an activity accepted the URL |
| `autojs6.device.info() -> dict[str, object]` | `device.info` | `{}` | strict `autojs6-python-device-info-v1` object |
| `autojs6.console.log(text: str) -> None` | `console.log` | `{"text": text}` | `null` |
| `autojs6.console.warn(text: str) -> None` | `console.warn` | `{"text": text}` | `null` |
| `autojs6.console.error(text: str) -> None` | `console.error` | `{"text": text}` | `null` |
| `autojs6.notice(text: str) -> None` | `notice.show` | `{"text": text}` | `null` |
| `autojs6.files.read_text(path, *, encoding="utf-8") -> str` | `files.read_text` | `{"path": path}` | bounded text |
| `autojs6.files.write_text(path, text, *, encoding="utf-8") -> None` | `files.write_text` | `{"path": path, "text": text}` | `null` |
| `autojs6.files.exists(path) -> bool` | `files.exists` | `{"path": path}` | existence |
| `autojs6.files.is_file(path) -> bool` | `files.is_file` | `{"path": path}` | regular-file test |
| `autojs6.files.is_dir(path) -> bool` | `files.is_dir` | `{"path": path}` | directory test |
| `autojs6.files.list(path=".") -> list[str]` | `files.list` | `{"path": path}` | sorted direct names |
| `autojs6.dialogs.alert(text, *, title="AutoJs6 Python") -> None` | `dialogs.alert` | `{"title": title, "text": text}` | `null` after acknowledgement or dismissal |
| `autojs6.dialogs.confirm(text, *, title="AutoJs6 Python") -> bool` | `dialogs.confirm` | `{"title": title, "text": text}` | positive action is `true`; negative/dismissal is `false` |
| `autojs6.dialogs.prompt(text, *, default="", title="AutoJs6 Python") -> str \| None` | `dialogs.prompt` | `{"title": title, "text": text, "default": default}` | entered text, or `null` on dismissal |
| `autojs6.dialogs.select(items, *, title="AutoJs6 Python") -> int \| None` | `dialogs.select` | `{"title": title, "items": items}` | zero-based index, or `null` on dismissal |
| `autojs6.engines.current() -> dict[str, object]` | `engines.current` | `{}` | strict current-engine identity without an absolute path |
| `autojs6.engines.run(path) -> dict[str, object]` | `engines.run` | `{"path": path}` | strict asynchronous child-execution handle |
| `autojs6.engines.stop_self() -> NoReturn` | `engines.stop_self` | `{}` | queues authoritative Host cancellation; never returns to following Python code |

Package names must use ordinary dotted Android identifier segments. URLs must
start with `http://` or `https://`. Empty toast/clipboard/console text is
allowed; package, application name, URL and notice text must be non-empty. A
notice is tagged with its execution UUID, uses the dedicated `autojs6-python`
channel and never opens a permission/settings UI. Missing Android permission or
a disabled app/channel returns `PERMISSION_DENIED`.

`device.info()` returns only the following strict pure-data shape:

```json
{
  "schema": "autojs6-python-device-info-v1",
  "battery": {"percent": 88.5, "charging": true},
  "screen": {"on": true, "brightness": 127},
  "volume": {
    "music": {"current": 7, "max": 15},
    "notification": {"current": 4, "max": 7},
    "alarm": {"current": 5, "max": 7}
  }
}
```

Battery percentage is in `[0, 100]`; brightness is the Android system value or
`-1` when unavailable. Every volume current/max pair is a non-negative integer
with `current <= max`. The Python facade rejects missing, extra or mistyped
fields as `BROKER_PROTOCOL_ERROR`.

The live Host-files root is the admitted project root for project execution and
the script's parent directory for standalone execution. Paths are NFC-normalized
relative UTF-8 text; `"."` names the root. Empty paths, absolute paths, Windows
drive prefixes, backslashes, control characters, empty segments, `.` segments
and `..` segments are rejected before dispatch. Canonical resolution must remain
inside the root, including when a symbolic link is present.

Only UTF-8 text is supported. Reads and writes are capped at 32 KiB encoded;
writes overwrite one regular file and require its parent directory to exist.
No parent creation, deletion, rename, recursion or binary I/O is implied.
Listings contain at most 128 validated direct child names and the Python facade
returns them in deterministic sorted order. Filesystem permission failures are
reduced to `PERMISSION_DENIED` or `HOST_FAILURE` without leaking Host internals.

Host dialogs reuse the same opaque foreground authorization boundary as
protocol 1.3 interactive input. Only an explicit user-gesture launch with a
live `Activity` receives a controller; scheduled tasks, ordinary background
project execution and other non-interactive launches have no controller and
return `INTERACTIVE_NOT_ALLOWED` before any UI is posted. The Host owns and
renders every `MaterialDialog`; Python receives only the typed pure-data result.

The foreground controller serializes one prompt or Host dialog at a time.
Cancel/back/dismiss maps to `false` for `confirm` and `None` for `prompt` and
`select`; alert dismissal completes with `None`. Execution cancellation closes
the current dialog and wakes the blocked call. Titles must be non-empty; dialog
content may be empty. Selection items must be non-empty text, and the Python
facade validates every byte/count limit before dispatch while the Host validates
it again. No dialog exposes a `Context`, view object, callback or raw Binder to
Python.

`engines.current()` returns exactly the
`autojs6-python-engine-info-v1` shape: `id`, `engineName`, `sourceName`,
`entryPoint`, `project`, and `startedAtMillis` plus the schema field. The engine
name is `python`; the ID and start time identify the current public Host engine.
`sourceName` is a bounded display name and `entryPoint` is a normalized relative
project entry or standalone filename. Neither field contains the execution-root
absolute path, and no Host engine or Java object crosses the broker.

`engines.run(path)` accepts the same NFC-normalized, execution-root-relative
path grammar as Host files and requires a canonical regular file inside that
root. The ordinary Host launch resolver selects the script type, working
directory and any project context, which must also remain inside the root. A
non-Python script is submitted asynchronously through `ScriptEngineService`;
the result is exactly the `autojs6-python-engine-launch-v1` shape with a
non-negative execution `id`, bounded `engineName`/`sourceName`, and the original
normalized relative `path`. It is a launch handle, not a completion result, and
does not grant inspection, cancellation or mutation of another engine.

The provider remains single-session, so a `.py` target cannot occupy a nested
session while its caller is active and fails with
`NESTED_PYTHON_NOT_ALLOWED`. Each parent execution may complete at most 16
successful child launches; a launch which fails before returning a valid handle
does not consume that success quota. The existing 1024-call and message limits
still apply independently.

`engines.stop_self()` queues `forceStop` on the Host main dispatcher. Host
cancellation is authoritative and retires the provider process under the
existing `PROCESS_RESTART_ONLY` mode. If the null broker response reaches
Python before cancellation, the facade immediately raises `SystemExit(0)` so
following user code still cannot execute. The next admitted Python execution
rediscovers a fresh provider process. No API is implied for enumerating all
engines, evaluating source text, launching an arbitrary absolute path, or
stopping another execution.

The launch-time `app.snapshot()` and `device.snapshot()` APIs remain detached
immutable snapshots. The execution-private workspace visible to ordinary Python
`open()` is still a frozen Plugin-side copy and is not mutated by
`autojs6.files`. Conversely, `autojs6.files` observes the live bounded Host root;
it does not grant arbitrary filesystem access, expose a general Java bridge, or
add accessibility, screenshot or OCR APIs. The bounded engines facade likewise
does not expose Host runtime objects. Those remaining capabilities stay separate
Roadmap items.

## Trust boundary

Python scripts are trusted local code for every permission and API they can
reach. Protocol 1.5 narrows the accidental cross-process surface but does not
turn Chaquopy into a hostile-code sandbox. User globals receive Python
functions, never Android `Context`, Host `ScriptRuntime`, callbacks or the raw
broker Binder. The Host validates the Binder calling UID before clearing its
identity, dispatches only an explicit allow-list, and replaces unexpected Host
exceptions with stable errors.

## Focused public-engine acceptance

`PythonU1R2AcceptanceInstrumentationTest#firstLowRiskHostCapabilitiesRoundTripThroughProtocol15Broker`
launches an admitted Python project through the ordinary Host script engine and
the real plugin. The script shows a toast, writes and reads a unique clipboard
marker, receives `False` for missing package/application launch targets, and
observes `INVALID_ARGUMENT` for an intentionally unsupported `ftp://` URL
without opening an external activity. A strict structured result proves the
round-trip values, the test restores the original Android `ClipData`, and the
normal project/private-snapshot cleanup is asserted.

The test passed on Sony XQ-AT72 (`QV710AF65F`, API 31, arm64-v8a, 4 KiB pages)
in 1.607 seconds and on an API 37 x86_64 emulator with 16 KiB pages in 7.183
seconds. Both reported `OK (1 test)`. These are focused current-tree smokes, not
release or full-device-matrix evidence.

`PythonU1R2AcceptanceInstrumentationTest#remainingFirstBatchHostCapabilitiesRoundTripThroughProtocol15Broker`
launches the same public engine path for live device data, all three console
levels and notice dispatch. It validates the exact device schema/ranges and
actual global-console levels. When notifications are allowed it verifies and
then cancels only the execution-tagged notification; otherwise it requires the
stable `PERMISSION_DENIED` result without changing device permission state.

On the `0.3.0-alpha.2` current tree, this second test passed in 1.047 seconds on
Sony XQ-AT72 (`QV710AF65F`, API 31, arm64-v8a, 4 KiB pages) and 1.268 seconds on
the API 37 x86_64 16 KiB-page emulator. Both devices took the allowed branch,
verified an active execution-tagged notification and removed only that test
notification. The paired original-slice regression also passed in 1.567 and
7.913 seconds respectively. Every run reported `OK (1 test)`.

`PythonU1R2AcceptanceInstrumentationTest#hostFilesRoundTripThroughProtocol15BrokerWithoutEscapingProjectRoot`
launches an admitted project through the same public engine path. It reads a
Host seed, writes and rereads live UTF-8 text, checks existence and file/directory
types, lists the project root, receives stable `PATH_NOT_FOUND` for a missing
file, and rejects `../` locally. The test also proves that the Host output file
exists after execution while the already-frozen Plugin workspace does not see
that write, then removes the temporary project.

On the `0.3.0-alpha.3` current tree, this Host-files test passed in 0.811 seconds
on Sony XQ-AT72 (`QV710AF65F`, API 31, arm64-v8a, 4 KiB pages) and 3.295 seconds
on the API 37 x86_64 16 KiB-page emulator. Both reported `OK (1 test)`. This is
focused dual-device current-tree acceptance, not a published release or a full
device matrix.

`PythonU1R2AcceptanceInstrumentationTest#foregroundDialogsRoundTripThroughProtocol15Broker`
launches a standalone file through `Scripts.runInteractive`, the public Host
engine and the real Plugin. It acknowledges an alert, accepts a confirmation,
replaces a prompt default and selects the second item, then verifies the exact
typed structured result and private transport cleanup. The companion
`backgroundDialogsFailClosedWithoutOpeningUi` test launches an admitted project
without foreground authorization and requires the stable
`INTERACTIVE_NOT_ALLOWED` result without opening a dialog.

On the `0.3.0-alpha.4` current tree paired to clean Host commit
`f9eef784855f64da4ac0a9f33ad89688b3f3bd03`, the foreground test passed in
1.838 seconds on Sony XQ-AT72 and 8.295 seconds on the API 37 emulator. The
background test passed in 0.988 and 0.936 seconds respectively. All four runs
reported `OK (1 test)`. APKs were installed with replacement semantics under
the existing SM003 identity; no package uninstall or app-data clear was used.

`PythonU1R2AcceptanceInstrumentationTest#hostEnginesExposeSafeCurrentMetadataAndLaunchScopedJavaScript`
launches an admitted Python project through the same public engine path. It
checks the exact path-free current-engine shape, asynchronously launches a
project-local JavaScript child which writes a live Host marker, validates the
typed child handle, and requires `NESTED_PYTHON_NOT_ALLOWED` for an existing
project-local `.py` target. The companion
`hostEngineStopSelfRetiresProviderAndPreventsFollowingCode` test writes a marker
before `stop_self`, proves the statement after it never runs, compares provider
PIDs, and immediately executes another successful Python project.

On the `0.3.0-alpha.5` current tree paired to clean Host commit
`0c4df640ed1a3e08cda72899d080f0ae01238df9`, the two tests passed together in
3.122 seconds on Sony XQ-AT72 and 4.566 seconds on the API 37 emulator. Four
non-interactive regressions covering the complete first slice, Host files and
background-dialog rejection then passed in 3.622 and 12.982 seconds. Every run
reported `OK`; the ABI-specific APKs were installed with `adb install -r -t`
under the existing SM003 identity without uninstalling packages or clearing app
data.
