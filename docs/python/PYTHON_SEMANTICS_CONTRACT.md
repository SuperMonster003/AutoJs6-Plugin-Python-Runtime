# Python execution semantics contract

Status: cumulative U1-R0 through U1-R2 contract plus the first M3 protocol 1.5
Host capability slice and the bounded Host-files and foreground-dialog portions
of its second slice, plus bounded current-engine/self-stop/non-Python child
launch operations, plus M4 Path A project-local pure-Python packages.
Historical R2 evidence remains covered through E2; the M1/M2 public Host paths
and focused M3 broker paths passed an API 31 / arm64-v8a / 4 KiB-page physical
device and an API 37 / x86_64 / 16 KiB-page emulator on 2026-08-23. Those
smokes are not a release or device-matrix claim.

This document distinguishes three facts which must not be collapsed:

1. syntax and builtins provided by CPython 3.13;
2. behavior implemented by the Plugin bootstrap;
3. behavior proven on Android through the Host/Binder/PFD path.

The U1-R0 fixture and local Python tests are portable evidence only. They do
not prove Chaquopy packaging or Android execution.

## Support vocabulary

| Term | Meaning |
| --- | --- |
| `VERIFIED_PORTABLE` | The checked-in fixture executes through the portable bootstrap and has an exact result assertion. |
| `IMPLEMENTED_NOT_GATED` | Code appears to provide the behavior, but U1 has no dedicated exact fixture or Android proof yet. |
| `UNSUPPORTED` | Current metadata or implementation explicitly does not provide it. |
| `PLANNED_U1_R1` | Required by the high-priority R1 implementation. |
| `PLANNED_U1_R2` | Deliberately deferred because it requires module-entry or live-I/O protocol work. |
| `OUT_OF_SCOPE` | Not promised by the current usability track or requires an independent admission model. |

A portable result may advance a historical U1 case only to `VERIFIED_PORTABLE`.
The former Android/device promotion levels are preserved in
[`docs/legacy/ROADMAP-u1-en.md`](../legacy/ROADMAP-u1-en.md); current product
milestones follow the lightweight validation convention in [`ROADMAP.md`](../../ROADMAP.md).

## Runtime and source contract

| Property | `0.1.0` historical behavior | Current U1 contract |
| --- | --- | --- |
| Implementation | Chaquopy 17.0.0 / CPython 3.13.9 in the Plugin process | Preserve unless a later release explicitly freezes another identity |
| Script mode | Source bytes compiled as a file-like `__main__` | Protocol 1.2 keeps file mode as the default and adds an explicit, capability-gated module mode for admitted projects |
| Source encoding | README declared UTF-8, while byte compilation could honor CPython encoding cookies | U1-R1 now accepts strict UTF-8 with optional UTF-8 BOM and rejects NUL, invalid UTF-8 and conflicting non-UTF-8 cookies before dispatch |
| Python grammar | CPython grammar selected by the packaged 3.13 runtime | Ordinary Python 3.13 syntax is supported when its imports/platform dependencies are available |
| Top-level await | Not enabled by ordinary `compile(..., "exec")` | Remains unsupported in file mode; use `asyncio.run()` |
| Python 2 syntax | Unsupported | Remains unsupported |
| Explicit result | No script-visible typed result API | Protocol 1.4 adds one strict bounded JSON value plus optional bounded, hash-manifested output artifacts; stdout is never parsed as a result |

The Host and Provider must validate the exact SOURCE length and SHA-256. U1-R1
adds strict text admission; it must not silently reinterpret Latin-1 or another
encoding merely because a PEP 263 cookie is present.

## Host project timeout admission

The current Host accepts an optional `timeout` property in an admitted Python
project's `project.json`. Its value is an exact positive JSON integer in
milliseconds. Strings, booleans, null, zero, negative values, decimals and
scientific notation are invalid project configuration. The Host default is
5 minutes and the largest configured value is 30 minutes. At dispatch, the
effective timeout is the smaller of the configured/default Host value and the
Provider's advertised maximum; the current Plugin maximum is also 30 minutes.

This property changes only the bounded execution deadline. It does not enable
background UI, interactive stdin, replay, concurrency or an unbounded
long-task mode. Standalone file launches continue to use the Host default.

## Execution globals and process state

For file-mode execution:

- `__name__ == "__main__"`;
- `__file__` is the normalized logical entry point, never a Plugin-private
  staging path;
- `__spec__` is `None`; `__package__` is `None` for a standalone/root entry and
  the normalized dotted parent for a nested project-package entry;
- `sys.argv[0]` is the logical entry point and later values are the bounded
  request arguments;
- a project uses its private workspace root as cwd;
- a project places the entry directory first and workspace root second on
  `sys.path`;
- a standalone SOURCE does not gain an implicit copy of its original parent
  directory.

For module-mode execution:

- the current Host exposes this mode through a strictly admitted project
  manifest such as `{"type":"python","entryMode":"module","main":"pkg.main"}`;
  an absent `entryMode` or the exact string `file` keeps the existing
  project-relative `.py` path form for `main`, while `module` requires the
  normalized dotted name and writes `autojs6.python.entryMode=module` into the
  execution configuration;
- the execution must have an explicitly admitted project workspace and a
  provider which advertises protocol 1.2 module-entry support;
- the request entry point is a normalized dotted ASCII module name such as
  `pkg.main`. Each segment must be a non-keyword Python identifier;
  `pkg.__init__` is rejected as an ambiguous package target. The source uses
  the exact lowercase `.py` suffix, and its directory/stem segments contain no
  literal dots, keeping file/module mapping reversible;
- the dotted name maps deterministically to the separately verified SOURCE
  path (`pkg.main` to `pkg/main.py`), and the staged file must match those
  SOURCE bytes exactly before user code starts;
- `runpy.run_module(name, run_name="__main__", alter_sys=True)` supplies normal
  module metadata: `__name__ == "__main__"`, `__package__ == "pkg"`, and
  `__spec__.name == "pkg.main"` for the example above;
- only the project root is prepended, so it is `sys.path[0]` and package-relative
  imports follow normal module resolution. During execution, `__file__` and
  `sys.argv[0]` are the Plugin-private staged module path as provided by
  `runpy`; structured tracebacks still expose only logical project-relative
  names;
- any pre-existing interpreter modules in the target top-level namespace are
  temporarily removed, the resolved module spec must point to the exact staged
  entry file, and the original namespace is restored afterward. This prevents
  a previously imported stdlib/package module from hijacking project module
  entry in the long-lived runtime process.

An absent entry-mode field decodes as file mode for backward compatibility.
The module-mode field is required-for-reader on the wire, so a pre-1.2 reader
rejects the request instead of silently running the dotted module name with
file semantics.

The bootstrap must restore `builtins.input`, `getpass.getpass`, stdout, stderr,
stdin, argv, cwd and `sys.path` on every terminal path. Project modules and
project importer-cache entries must
not leak into a later execution. U1-R1 adds exact sequential-workspace tests
for same-named modules.

## Builtins and syntax

Ordinary CPython builtins and grammar do not require one wrapper per function.
U1 nevertheless keeps representative executable cases so that bootstrap
changes cannot silently break them. The minimum matrix includes:

- literals, Unicode, arithmetic, comparisons and boolean operators;
- `if`, `for`, `while`, comprehensions and generator expressions;
- functions, defaults, closures, lambdas, decorators and classes;
- context managers, exceptions, `ExceptionGroup` and `match`/`case`;
- async functions executed under `asyncio.run()`;
- `print`, `len`, `range`, `enumerate`, `zip`, `sum`, `min`, `max`, `open` in a
  project workspace, and bounded exit through `SystemExit`.

Passing this representative matrix is not a promise that an Android-specific
or omitted stdlib dependency exists. The packaged-runtime inventory and device
evidence remain separate.

## stdin and `input()`

### Historical `0.1.0`

- Provider metadata advertises `supportsStdinSnapshot=false` and
  `maxStdinBytes=0`.
- The Host sends no stdin payload.
- The bootstrap does not install an execution-local stdin.
- Therefore `input()` is unsupported. Depending on the underlying process
  stdin is neither a defined EOF nor a safe interactive interface, and must not
  be advertised.

### Current U1-R1 static snapshot implementation

- Reuse the existing optional `STDIN` payload reference and PFD contract.
- Verify payload kind, descriptor uniqueness, length, EOF, SHA-256,
  reliable-pipe errors and the Provider limit before CPython starts.
- Install a per-execution UTF-8 text stream whose `.buffer` exposes the bounded
  raw snapshot.
- Advertise `supportsStdinSnapshot=true` with a 1 MiB Provider maximum only
  after Host negotiation, private snapshot transport and Provider staging are
  present.
- `input(prompt)` writes its prompt to captured stdout and follows normal
  Python line/EOF behavior.
- Missing or empty input reaches EOF immediately; it never reads global
  process stdin and never waits for UI.
- Always restore the previous `sys.stdin` reference at cleanup.

### Current Host project declaration

The current paired Host exposes the existing finite snapshot channel to an
explicitly admitted Python project's `project.json`:

- `"stdin": "literal text"` always means inline text. The Host never guesses
  that a string naming an existing file is a path. An explicit empty string is
  retained as a present zero-byte snapshot.
- `"stdin": {"file": "fixtures/input.txt"}` explicitly selects the exact
  bytes of a project-relative regular file. The object must contain exactly
  the string property `file`; `text` aliases, extra properties and all other
  JSON shapes are invalid.
- A file name must be a Unicode NFC-normalized, forward-slash relative path no
  longer than 4 KiB in UTF-8. Absolute paths, URI-like names, backslashes,
  control characters, empty or `.` / `..` segments, symbolic links, missing
  paths and non-regular files fail closed.
- Inline and file snapshots are bounded by the current Provider maximum of
  1 MiB. The manifest itself retains its separate 64 KiB limit. The file is
  read with a bounded loop while the unified Launch creates its execution
  configuration, so subsequent file edits do not mutate that execution's
  pre-supplied bytes.
- The admitted declaration is retained on `PythonProjectSource` and rechecked
  immediately before private transport. The Host writes the existing
  `autojs6.python.stdinSnapshot` argument, so this public entry requires no new
  Binder or tagged-wire field. An absent `stdin` leaves the argument absent.
- Standalone-file launches still have no public manifest or UI for supplying a
  snapshot. Foreground built-in `input()` remains the separate interactive
  path described below.

The public Host engine path was accepted with project-file stdin, Unicode
`sys.stdin.read()`, deterministic repeated-read EOF and private-snapshot
cleanup on Sony XQ-AT72 (`QV710AF65F`, API 31, arm64-v8a, 4 KiB pages) and an
API 37 x86_64 emulator with 16 KiB pages. The paired Host implementation is
commit `e3a5b6da3`; this is current-tree device acceptance, not stable-release
provenance.

The snapshot path above is finite pre-supplied input. The foreground
prompt/reply loop below is interactive input and remains a separate channel.

### Current U1-R2 foreground interactive implementation

- A live prompt/reply loop is authorized only by an opaque grant minted in an
  explicit foreground user-gesture Host launch with a live `Activity`.
  Background launches never open UI and keep the immediate-EOF behavior above.
- Protocol 1.3 advertises `supportsInteractiveInput` and nonzero prompt, reply,
  count and wait ceilings. An interactive request carries a narrower policy in
  a required-for-reader field so a pre-1.3 reader fails closed.
- The built-in `input()` and standard-library `getpass.getpass()` consume the
  finite snapshot first. Only after snapshot EOF do they issue a typed prompt
  with an execution request ID, positive monotonic prompt ID, bounded text,
  visible/hidden echo policy, reply byte ceiling and monotonic deadline.
- `input()` requests visible echo and writes its prompt to captured stdout.
  `getpass.getpass(prompt="Password: ", stream=None)` requests hidden echo and
  writes its prompt to the supplied stream, or captured stderr when no stream is
  supplied. The Host password dialog disables visible characters and keyboard
  suggestions.
- Exactly one matching `VALUE`, `EOF`, or `CANCELLED` reply is accepted.
  `VALUE` permits an empty string; `EOF` raises `EOFError`; `CANCELLED` raises
  `KeyboardInterrupt`. Duplicate, unsolicited, reordered, mismatched or
  oversized replies fail closed.
- `sys.stdin.read*()` and `sys.stdin.buffer` remain finite snapshot APIs and do
  not invoke the live bridge. This feature is interactive built-in input, not
  a claim of general live stdin.
- Cancellation, execution timeout, callback Binder death, close, service
  destruction and runtime-generation retirement clear the pending prompt and
  wake the Plugin wait. Host terminal/connection/plugin-state paths interrupt
  the separate bounded UI task and dismiss its dialog.
- The original built-in, original `getpass.getpass`, and stdio/process state are
  restored on all terminal paths. The Host dialog/controller never crosses Binder and the narrow
  Plugin bridge is never placed in Python globals.

The paired public Host entry paths were accepted with real Host-owned dialogs
and the real CPython Plugin on Sony XQ-AT72 (`QV710AF65F`, API 31,
arm64-v8a, 4 KiB pages) and an API 37 x86_64 emulator with 16 KiB pages. The
test follows the editor's `Scripts.runWithBroadcastSenderInteractive` entry and
Explorer's `Scripts.runInteractive` entry, verifies visible versus password
accessibility nodes, submits bounded replies, validates the structured results,
and proves that neither reply appears in the global console. The paired Host
implementation/evidence commit is `70ea17097`; this remains current-tree
acceptance rather than stable-release provenance.

The detailed wire and lifecycle rules are in
`docs/python/U1_R2_INTERACTIVE_INPUT_PROTOCOL.md`.

## Import contract

### Builtin, frozen and standard-library modules

`import` uses the packaged CPython runtime. Pure stdlib availability must be
verified from the APK/runtime rather than inferred from desktop Python.
Android- or native-dependent modules are reported separately. A portable
`import json` result is E1, not Android proof.

### Project modules and packages

An admitted Python project is snapshotted into a private workspace. Its entry
directory and project root are the only project import roots added by the
bootstrap. U1-R1 covers:

- entry-sibling and project-root modules;
- regular and namespace packages;
- re-exports, circular imports and `importlib.import_module`;
- exact cleanup between sequential projects.

An archive never shadows the separately verified entry SOURCE. Project paths
and traceback frames are logical relative names; private staging roots do not
cross the result boundary.

### Standalone source

A standalone `.py` snapshot contains only that source. The Plugin must not
copy its arbitrary parent directory because doing so could read unrelated
files, exceed bounded transport, or create a race-dependent import surface.
Sibling imports require an explicitly admitted Python project. A future Host
UX may help users run a file with its explicit project context, but cannot
silently widen the snapshot.

### Relative imports and module entry

A standalone/root file-mode `__main__` has no package context. For a nested
entry inside an explicitly admitted project, U1-R1 derives only normalized
identifier parent segments as `__package__`; this permits ordinary relative
imports such as `from .helper import VALUE` without widening the workspace.
`__spec__` remains `None` in file mode.

U1-R2 adds the distinct `entryMode=module` behavior described above. It is
selected explicitly, backed by `runpy`, and never silently replaces file mode.
Module mode places only the project root at `sys.path[0]`, preserves standard
package discovery and module metadata, and supports ordinary package-relative
imports without widening the admitted workspace.

### Third-party dependencies

The embedded runtime remains stdlib-only. M4 Path A adds project-local
pure-Python distributions: an admitted project may place import packages and
their `.dist-info` metadata directly in its root, which is already first on
`sys.path` during project execution. Ordinary transitive imports and
`importlib.metadata` discovery then work from the immutable workspace snapshot;
the packages do not become part of the Plugin runtime or its dependency lock.

M4 Path B evaluated embedding the pinned five-distribution `requests` closure
at build time and recorded `NOT_ADMITTED` in ADR 0003. No Chaquopy pip block,
build-time package payload or candidate license is part of the current APK.
The decision preserves `python.packages.policy=stdlib-only`, package count zero
and `online.pip.allowed=false`; it is not a claim that the candidate cannot run
under Chaquopy. A future build-time package must first satisfy ADR 0003's
immutable wheel, exact hash, offline build, license, APK-size and dual-ABI gate.

The Host admits at most a 64 MiB compressed workspace, 8192 archive file
entries and 128 MiB of extracted file content. Provider selection compares the
actual snapshot against all three advertised capacities before dispatch. These
bounds include project source and data as well as dependency files.

An absent third-party package still raises ordinary `ModuleNotFoundError`.
No import failure may trigger online pip, a runtime download or another engine.
Starting with `0.2.0`, stdlib and project-local clients may make
script-initiated network connections because the Plugin declares Android's
normal `INTERNET` permission; that permission does not install packages or
fetch code automatically. Arbitrary native wheels remain unsupported until a
package has a separate Android, ABI and page-size admission path.

Preparation instructions, reproducibility guidance and failure behavior are
defined in `docs/python/PROJECT_LOCAL_PACKAGES.md`.

The focused public Host acceptance used a pinned five-distribution `requests`
tree and constructed 1100 workspace files, 33 MiB of compressible content and
17 MiB of deterministic random content. A successful dispatch therefore
crossed the former 1024-entry, 16 MiB compressed and 32 MiB extracted bounds.
It imported all five project-local distributions, completed HTTPS with status
200 and matched their exact metadata versions. On the `0.3.0-alpha.6` current
tree the test passed in 5.040 seconds on Sony XQ-AT72 (`QV710AF65F`, API 31,
arm64-v8a, 4 KiB pages) and 5.406 seconds on the API 37 x86_64 emulator with
16 KiB pages. Both runs reported `OK (1 test)` after `adb install -r -t` and
retained application data; this is focused current-tree acceptance rather than
a complete package, ABI or release matrix.

## Live Host capabilities (protocol 1.5)

Protocol 1.5 adds an execution-scoped, synchronous Host capability broker. The
Provider advertises `supportsHostCapabilityBroker=true`; negotiation below 1.5
continues through the historical `openSession` AIDL transaction with no live
broker, while a 1.5 session requires the appended
`openSessionWithHostCapabilities` transaction and exactly one live broker.

The current public Python surface is:

- `autojs6.toast(text: str) -> None`;
- `autojs6.clip.get() -> str` and `autojs6.clip.set(text: str) -> None`;
- `autojs6.app.launch(package_name: str) -> bool`;
- `autojs6.app.launch_app(name: str) -> bool`;
- `autojs6.app.open_url(url: str) -> bool` for HTTP(S) URLs.
- `autojs6.device.info() -> dict[str, object]` for current battery, charging,
  screen-on, brightness and music/notification/alarm volume pairs;
- `autojs6.console.log/warn/error(text: str) -> None` for direct level-aware
  Host global-console output;
- `autojs6.notice(text: str) -> None` for one execution-tagged notification.
- `autojs6.files.read_text(path, *, encoding="utf-8") -> str` and
  `autojs6.files.write_text(path, text, *, encoding="utf-8") -> None`;
- `autojs6.files.exists/is_file/is_dir(path) -> bool` and
  `autojs6.files.list(path=".") -> list[str]` for the live Host execution root.
- `autojs6.dialogs.alert(text, *, title="AutoJs6 Python") -> None`;
- `autojs6.dialogs.confirm(text, *, title="AutoJs6 Python") -> bool`;
- `autojs6.dialogs.prompt(text, *, default="", title="AutoJs6 Python") -> str | None`;
- `autojs6.dialogs.select(items, *, title="AutoJs6 Python") -> int | None`;
- `autojs6.engines.current() -> dict[str, object]` for path-free current Host
  engine metadata;
- `autojs6.engines.run(path) -> dict[str, object]` for an asynchronous scoped
  non-Python Host child launch;
- `autojs6.engines.stop_self() -> NoReturn` for deterministic Host cancellation;
- `autojs6.automator.click(x: int, y: int) -> bool` and
  `autojs6.automator.long_click(x: int, y: int) -> bool`;
- `autojs6.automator.press(x: int, y: int, duration_ms: int = 100) -> bool`;
- `autojs6.automator.swipe(x1: int, y1: int, x2: int, y2: int,
  duration_ms: int = 300) -> bool`;
- `autojs6.automator.back() -> bool` and `autojs6.automator.home() -> bool`;
- `autojs6.selector.snapshot(max_nodes: int = 64, max_depth: int = 16)
  -> dict[str, object]` for a bounded breadth-first UI tree;
- `autojs6.selector.find(*, text=None, text_contains=None, description=None,
  description_contains=None, resource_id=None, class_name=None, clickable=None,
  editable=None, enabled=None, scrollable=None, max_nodes=512, max_depth=32)
  -> dict[str, object] | None` for an AND-composed first match;
- `autojs6.selector.click(node: str | dict[str, object]) -> bool` and
  `autojs6.selector.set_text(node: str | dict[str, object], text: str) -> bool`;
- `autojs6.images.capture_screen(*, format="png", quality=100, path=None)
  -> bytes | str`;
- `autojs6.images.find_color(color, *, region=None, threshold=0)
  -> tuple[int, int] | None`;
- `autojs6.images.find_image(template, *, region=None, threshold=0)
  -> tuple[int, int] | None`;
- `autojs6.ocr.recognize(image) -> tuple[str, ...]` through the configured Host
  OCR engine.

These are live Host operations, distinct from the detached launch-time
`app.snapshot()` and `device.snapshot()` data. Every request is bound to the
canonical execution request UUID and a positive monotonic call ID. The Host
also pins the Plugin UID, admits at most 1024 calls, bounds request/response
documents to 64 KiB and text to 32 KiB, and bounds an ordinary Host main-thread
action to 5 seconds. Calls are serialized by the Python facade and block until
a typed response arrives. A foreground dialog may wait for one user response
for at most 5 minutes and remains independently bounded by the overall execution
deadline.

Missing/closed capabilities raise `CapabilityUnavailableError`. Host and wire
failures raise `HostCapabilityError`, whose `code` property is stable. Cleanup
revokes both the private Java bridge and execution-local Python state, including
copied contexts; a call is never replayed after cancellation or connection
loss. The detailed JSON schemas, error codes, lifecycle and exact capability
mapping are in `HOST_CAPABILITY_BROKER_PROTOCOL.md`.

Notice text is non-empty and at most 4 KiB UTF-8. The API never requests a
permission or opens settings: Android permission, app-level notification or
channel denial raises `HostCapabilityError` with code `PERMISSION_DENIED`.
`device.info()` uses the strict schema documented in
`HOST_CAPABILITY_BROKER_PROTOCOL.md`; malformed, extra or mistyped result fields
are rejected as `BROKER_PROTOCOL_ERROR`.

Host dialogs require the opaque Activity-backed foreground grant already used
by protocol 1.3 input. Background and scheduled launches never open dialog UI;
they receive `HostCapabilityError.code == "INTERACTIVE_NOT_ALLOWED"`. The Host
renders and owns one serialized dialog at a time. Alert produces `None` after
acknowledgement/dismissal; confirmation returns `True` only for the positive
action; prompt and selection return `None` on cancel/back/dismiss, otherwise
text or a zero-based index.

Dialog titles are non-empty and at most 256 UTF-8 bytes; content is at most
4 KiB; prompt defaults and replies are at most 32 KiB. Selection accepts 1-64
non-empty items, each at most 1 KiB and at most 32 KiB in aggregate. The Python
facade rejects invalid values before dispatch, and the Host repeats the bounds.
Cancellation closes the current Host dialog and wakes the blocked call. No view,
Context, callback or Binder handle is exposed to Python.

`engines.current()` returns one strict `autojs6-python-engine-info-v1` mapping
with the current public Host execution ID, the `python` engine name, a bounded
display source name, a normalized relative entry point, a project flag and the
Host start time. It exposes neither the execution-root absolute path nor an
engine/Java object. `engines.run(path)` accepts only the same normalized
execution-root-relative path grammar as Host files, requires a canonical regular
file inside that root, and delegates type selection to the ordinary Host launch
resolver. It returns a strict `autojs6-python-engine-launch-v1` handle immediately
after a non-Python child is submitted; the handle is not a completion result and
does not grant control of the child.

The provider still admits only one active Python session. Selecting a Python
target from `engines.run` therefore raises `HostCapabilityError` with stable code
`NESTED_PYTHON_NOT_ALLOWED`. One parent execution may successfully submit at
most 16 child scripts; failed launch attempts do not consume the success quota,
and the existing 1024-call quota remains independent. `engines.stop_self()`
queues Host `forceStop`, which uses the existing process-restart-only cancellation
mode. If the broker response wins the race, the Python facade raises
`SystemExit(0)` before any following statement.

Automator coordinates are strict non-boolean integers from 0 through 1,000,000.
Press and swipe durations are strict non-boolean integers from 1 through 4,000
milliseconds. The Python facade rejects invalid values before dispatch, and the
Host repeats the same bounds. Each method returns the actual boolean result from
the Host accessibility action; false is not rewritten or retried. If the AutoJs6
accessibility service is missing, disconnected or not operational, the Host
returns stable `ACCESSIBILITY_UNAVAILABLE`, which the Python facade maps to
`CapabilityUnavailableError`. The API never enables accessibility or opens
settings. Selector/UI-tree access is a separate bounded surface; screenshots and
OCR remain separate from the coordinate action API. The complete bounded
coordinate/global surface is documented in `HOST_AUTOMATOR.md`.

`selector.snapshot` returns strict schema `autojs6-python-ui-tree-v1` with a
positive generation, an honest `truncated` flag, and breadth-first detached node
mappings. A snapshot defaults to 64 nodes/depth 16, accepts at most 128
nodes/depth 32, and caps its JSON value at 48 KiB. Node text, description,
resource ID, class name and package name are nullable and capped at 256 Unicode
code points; `truncatedFields` explicitly names shortened fields. Bounds,
parent/depth relationships and accessibility state flags are plain JSON values.

`selector.find` requires at least one condition and combines all supplied exact,
literal-substring and boolean predicates with AND. It performs a breadth-first,
case-sensitive scan of at most 512 nodes by default and at most 1024 nodes/depth
32 when requested. Exhaustive absence returns `None`; hitting a node/depth bound
before proving absence returns stable `SELECTOR_SCAN_LIMIT_EXCEEDED`. Query text
is non-empty and capped at 1024 UTF-8 bytes. It does not poll, wait, interpret a
regular expression, climb to a clickable ancestor or retry.

Selector IDs are opaque execution-local references rather than serialized
Android objects. A new snapshot invalidates the previous generation, `find`
retains returned nodes up to a 128-node FIFO bound, window-invalid nodes must
refresh before action, and broker cleanup recycles the entire set. An unknown,
evicted, invalidated or unrefreshable reference returns stable `STALE_NODE`.
`click` and `set_text` return the actual platform boolean without fallback;
text-setting accepts at most 4096 UTF-8 bytes. Accessibility unavailability uses
the same fail-closed `CapabilityUnavailableError` mapping as automator. The full
schema and lifetime contract is documented in `HOST_SELECTOR.md`.

`images.capture_screen(*, format="png", quality=100, path=None)` requires Android
11 or newer plus an enabled, connected and operational AutoJs6 accessibility
service. It accepts only exact `png`/`jpeg` formats and a strict non-boolean
quality from 1 through 100. With no path it returns immutable encoded bytes;
with a normalized execution-relative path it atomically writes and publishes an
ordinary output artifact, returning the Plugin-private absolute path. The API
never enables accessibility, opens settings, invokes MediaProjection or shows a
screen-sharing permission prompt.

The Host retains at most one execution-local encoded image and exposes it only
through exact `autojs6-python-screen-image-v1` and
`autojs6-python-screen-image-chunk-v1` pure-data mappings. Width and height are
each capped at 8192, total area at 16,777,216 pixels, encoded size at 4 MiB, and
raw transfer chunks at 32 KiB (at most 128 chunks). Python validates exact
fields, format, bounds, ordered offsets, canonical Base64, EOF, byte length,
SHA-256 and PNG/JPEG signatures before returning or writing the image. A valid
opaque image ID is always released; replacement, release and broker terminal
zero Host-retained bytes, while Python zeroes its mutable assembly buffer after
copy/write or failure.

`images.find_color(color, *, region=None, threshold=0)` takes one fresh Android
11+ accessibility screenshot and performs the complete search inside the Host.
`color` is a strict non-boolean integer from `0x000000` through `0xFFFFFF` or
exact `#RRGGBB` text. `threshold` is a strict integer from 0 through 255 and is
applied independently to the absolute red, green and blue channel differences;
pixel alpha is ignored. An optional tuple/list `(x, y, width, height)` uses
non-negative origins and positive sizes inside the fixed 8192-pixel dimension
bound, and the Host also requires it to fit the captured screen.

Search order is deterministic top-to-bottom then left-to-right. The first match
returns an absolute `(x, y)` tuple and exhaustive absence returns `None`. The
strict `autojs6-python-color-match-v1` result requires exact fields, a boolean
found flag, canonical `-1/-1` miss coordinates, bounded hit coordinates and
requested-region containment. No encoded screenshot, pixel row, image handle or
Android object crosses into Python; the Host clears its bounded row buffer and
recycles the screenshot in `finally`. Color search does not occupy or replace
the one retained encoded-image slot used by `capture_screen`.

`images.find_image(template, *, region=None, threshold=0)` accepts PNG/JPEG
`bytes`, `bytearray` or a byte-oriented `memoryview` and returns the absolute
top-left `(x, y)` of the first exact-size template candidate in deterministic
top-to-bottom/left-to-right order, or `None` after exhaustive absence. Region
and threshold use the same strict local and repeated Host validation as
`find_color`. The Host compares absolute RGB channel differences and treats only
decoded template pixels with alpha exactly 255 as participating pixels; every
other pixel is a wildcard, and at least one fully opaque pixel is required.

Python identifies the encoded format, copies the template into a mutable
temporary buffer, declares byte length and SHA-256, and uploads ordered canonical
Base64 chunks of at most 24 KiB through exact
`autojs6-python-image-template-v1` and
`autojs6-python-image-template-chunk-v1` responses. Encoded bytes are capped at
1 MiB; decoded dimensions at 2048 each and decoded area at 1,048,576 pixels.
The screenshot search region is capped at 4,194,304 pixels and one search at
16,777,216 counted anchor/full comparisons. Exceeding a bound fails rather than
returning a false miss.

The Host owns at most one pending or decoded execution-local template and clears
encoded/pixel/offset arrays on replacement, upload/decode failure, release, or
broker terminal. Python releases every usable ID in `finally` and overwrites its
mutable upload copy. A successful match uses exact
`autojs6-python-image-match-v1`; Python verifies hit/miss consistency, fixed
coordinate bounds, and full template containment in a requested region. Host
decode uses Android `BitmapFactory`; matching does not load, require, or fall
back to the AutoJs6 OpenCV plugin.

Android/API or capture-service absence maps to `CapabilityUnavailableError` via
`SCREEN_CAPTURE_UNAVAILABLE` or `ACCESSIBILITY_UNAVAILABLE`. Platform capture or
search/encoding failure returns `SCREEN_CAPTURE_FAILED`; size, region, or
comparison overflow returns `RESULT_LIMIT_EXCEEDED`. Unavailable execution-local
handles return `STALE_IMAGE` or `STALE_TEMPLATE`, while invalid template bytes,
digest/decode/dimensions, or an all-wildcard template return
`INVALID_IMAGE_TEMPLATE`. Malformed transfer, acknowledgement, color-match, or
template-match data returns `BROKER_PROTOCOL_ERROR`.
Android image objects and callbacks never cross the process boundary. Mutable
images, cropping, arbitrary pixel access, capture-to-template handles, and
multi-scale/rotated matching remain undeclared. The full transfer, search,
error and artifact contract is documented in `HOST_IMAGES.md`.

`ocr.recognize(image)` accepts the same PNG/JPEG bytes-like values and bounded
upload envelope as `images.find_image`: 1 MiB encoded, 24 KiB ordered chunks,
2048 pixels per side, 1,048,576 decoded pixels, and at least one alpha-255
pixel. It returns an immutable tuple in the exact line order supplied by the
Host-selected OCR plugin. Empty recognition is `()`; Python does not trim,
merge, sort, deduplicate, or infer text.

The Host selects only an enabled, authorized and Host-compatible service from
its existing OCR plugin host, respecting configured variant priority. It copies
the retained pixels into a temporary `ARGB_8888` bitmap, clears the copied
array, invokes the existing line-oriented OCR AIDL path, then erases/recycles
the bitmap. Python always releases the upload and clears its mutable copy. No
OCR implementation/model, Android bitmap, Binder, plugin object, or callback
crosses into Python, and the API never installs/enables/authorizes a service or
opens settings.

Recognition is limited to 256 lines, 4 KiB strict UTF-8 per line, and 48 KiB of
aggregate line text, in addition to the 64 KiB encoded broker-response limit.
The Host validates external output and Python repeats the checks. No eligible
engine returns stable `OCR_UNAVAILABLE`, mapped to
`CapabilityUnavailableError`; selected-engine failure returns `OCR_FAILED`;
image/result overflow uses `RESULT_LIMIT_EXCEEDED`, stale upload lifetime uses
`STALE_TEMPLATE`, invalid upload/decode uses `INVALID_IMAGE_TEMPLATE`, and a
malformed result uses `BROKER_PROTOCOL_ERROR`. Detection boxes, confidence,
orientation, engine/language/profile options, preprocessing, and a direct
capture-to-OCR handle remain undeclared. The full contract is documented in
`HOST_OCR.md`.

Android rejects accessibility screenshot requests made within 333 ms of the
previous accepted request. Only exact
`ERROR_TAKE_SCREENSHOT_INTERVAL_TIME_SHORT` is retried: the Host waits 350 ms,
allows at most three total attempts, and keeps every attempt inside the same
four-second capture deadline. Every other platform error, interruption,
deadline exhaustion, or unavailable service remains fail-closed without retry.

Focused screen-capture acceptance exercised the public Python project engine
against Host 5276 and Plugin `0.4.0-alpha.3`/57. On the API 37 x86_64 16
KiB-page emulator, an accessibility-enabled run captured the controlled UI to
`screens/python-capture.png`, decoded the published PNG, matched its target
`#123456` pixel, enforced the 4 MiB bound, and proved that the Python payload,
Plugin reconstruction and Host artifact had identical lengths and SHA-256
values. It completed in 5.867 seconds with `OK (1 test)`. On Sony XQ-AT72
(`QV710AF65F`, API 31, arm64-v8a, 4 KiB pages), `images.capture_screen()` failed
closed with the exact `CapabilityUnavailableError`, published no artifact and
left the pre-existing six-service accessibility list byte-for-byte unchanged;
that run completed in 0.866 seconds with `OK (1 test)`. Neither run uninstalled
packages or cleared application data, and this is focused current-tree
acceptance rather than a release claim.

Focused color-search acceptance exercised the public Python project engine
against Host 5276 and Plugin `0.4.0-alpha.4`/60. On the API 37 x86_64 16
KiB-page emulator, an accessibility-enabled run searched only the controlled
target bounds with per-channel threshold 2, found the `#123456` target inside
that region, returned no image artifact, and completed in 5.707 seconds with
`OK (1 test)`. On Sony XQ-AT72 (`QV710AF65F`, API 31, arm64-v8a, 4 KiB pages),
`images.find_color(0x123456)` failed closed with the exact
`CapabilityUnavailableError` while the pre-existing six-service accessibility
list remained byte-for-byte unchanged; it completed in 0.945 seconds with
`OK (1 test)`. Neither run uninstalled packages or cleared application data.
The emulator service was restored to enabled, bound, non-binding and non-crashed
state after instrumentation; this remains focused current-tree acceptance rather
than a release claim.

Focused template-search acceptance exercised the public Python project engine
against Host 5276 and Plugin `0.4.0-alpha.5`/63. On the API 37 x86_64 16
KiB-page emulator, one execution uploaded a 3 x 3 PNG target, searched only the
controlled `#123456` bounds with per-channel threshold 2, returned a contained
top-left coordinate, then immediately uploaded a second PNG and proved
exhaustive absence returned `None`. The back-to-back captures also exercised
the bounded 350 ms retry for Android's 333 ms screenshot throttle. The final
run completed in 5.841 seconds with `OK (1 test)`, and Host, test and Plugin
code paths remained unchanged across instrumentation. On Sony XQ-AT72
(`QV710AF65F`, API 31, arm64-v8a, 4 KiB pages), `images.find_image(...)`
failed closed with the exact `CapabilityUnavailableError` in 0.979 seconds;
`accessibility_enabled=1` and the pre-existing six-service list remained
byte-for-byte unchanged with AutoJs6 absent. Neither run uninstalled packages
or cleared application data. The emulator was restored to the one enabled and
bound AutoJs6 service with empty binding/crashed sets; this remains focused
current-tree acceptance rather than a release claim.

Focused Host-OCR acceptance exercised the public Python project engine against
Host 5276 and Plugin `0.4.0-alpha.6`/66. On the API 37 x86_64 16 KiB-page
emulator, an SM003-signed ML Kit OCR `1.0.0`/4 service recognized an
instrumentation-generated 1200 x 320 PNG containing `AUTOJS6 OCR 2026` through
the configured `OcrPluginHost` path. Python returned an immutable tuple whose
combined text contained all three controlled tokens, published no artifact,
and completed in 2.873 seconds with `OK (1 test)`. Accessibility remained
disabled with a null service list before and after; Host, test and Python
Runtime processes did not remain after instrumentation. The verified OCR test
dependency remains installed on that emulator rather than being uninstalled.
On Sony XQ-AT72 (`QV710AF65F`, API 31, arm64-v8a, 4 KiB pages), no OCR service
was installed and the same public API failed closed with the exact
`CapabilityUnavailableError` message in 0.918 seconds. Its
`accessibility_enabled=1` state and pre-existing six-service list remained
byte-for-byte unchanged with AutoJs6 absent. Installs used only
`adb install --no-streaming -r -t`; no package was uninstalled, no app data was
cleared, and this remains focused current-tree acceptance rather than a release
claim.

Focused selector acceptance exercised the public Python project engine against
the paired Host 5276 and Plugin `0.4.0-alpha.2`/54 builds. On the API 37 x86_64
16 KiB-page emulator, an accessibility-enabled run validated the bounded tree
schema and resource IDs, AND-composed first matches, exhaustive absence,
click/set-text platform results and independent UI latches, then proved that a
new snapshot invalidated the prior node with exact `STALE_NODE`. It completed in
4.863 seconds with `OK (1 test)`. On Sony XQ-AT72 (`QV710AF65F`, API 31,
arm64-v8a, 4 KiB pages), `selector.snapshot` failed closed with the exact
`CapabilityUnavailableError` while the pre-existing six-service accessibility
list remained byte-for-byte unchanged; that run completed in 0.869 seconds with
`OK (1 test)`. Neither run uninstalled packages or cleared application data,
and this is focused current-tree acceptance rather than a release claim.

The focused public Host acceptance invoked the six current method names through
a real protocol 1.5 session on Sony XQ-AT72 (`QV710AF65F`, API 31, arm64-v8a,
4 KiB pages) and an API 37 x86_64 emulator with 16 KiB pages. It verified toast
dispatch, clipboard round-trip and restoration, `False` launch results for
missing targets, a stable `INVALID_ARGUMENT` result for a rejected non-HTTP(S)
URL, strict structured output and private transport cleanup. The runs completed
in 1.607 and 7.183 seconds respectively with `OK (1 test)`; this is focused
current-tree acceptance, not a release claim.

The paired complete-first-slice test queried and schema-validated live device
state, wrote distinct debug/warn/error Host console entries, and posted then
removed an execution-tagged notice. On the `0.3.0-alpha.2` current tree it
passed on the same physical device and emulator in 1.047 and 1.268 seconds;
both devices took the notification-allowed branch. The original six-call test
also regressed green in 1.567 and 7.913 seconds. All four runs reported
`OK (1 test)` and retained normal private-snapshot cleanup.

The bounded Host-files public-engine test then read and wrote the live project
root, checked existence/types/direct listing, required stable `PATH_NOT_FOUND`,
rejected parent traversal, and proved the write remained absent from the frozen
Plugin workspace snapshot. On the `0.3.0-alpha.3` current tree it passed on the
same physical device and emulator in 0.811 and 3.295 seconds respectively; both
runs reported `OK (1 test)` and removed the temporary Host project.

The foreground-dialog public-engine test then exercised alert, positive
confirmation, prompt default replacement and zero-based selection through a
real Host-owned `MaterialDialog` chain. On the `0.3.0-alpha.4` current tree it
passed on the same physical device and emulator in 1.838 and 8.295 seconds.
The paired background project required `INTERACTIVE_NOT_ALLOWED` without UI and
passed in 0.988 and 0.936 seconds. All four runs reported `OK (1 test)`, used
clean Host commit `f9eef784855f64da4ac0a9f33ad89688b3f3bd03`, and retained normal
private-snapshot cleanup.

The engines public-engine pair then checked the exact path-free current mapping,
launched a project-local JavaScript child and observed its live Host marker,
required `NESTED_PYTHON_NOT_ALLOWED` for a project-local `.py` target, and proved
that `stop_self` prevented the following statement, changed the provider PID and
allowed an immediate successful Python restart. On the `0.3.0-alpha.5` current
tree paired to clean Host commit `0c4df640ed1a3e08cda72899d080f0ae01238df9`,
the two tests passed together in 3.122 seconds on the physical device and 4.566
seconds on the emulator. Four non-interactive first-slice/files/background-dialog
regressions passed in 3.622 and 12.982 seconds. All runs reported `OK`; installs
used `adb install -r -t` with the existing signer and retained application data.

The bounded-automator public-engine pair used Host commit `843f528bb` and the
`0.4.0-alpha.1` Plugin candidate. On the API 37 x86_64 16 KiB-page emulator,
the accessibility-enabled test required true results from click, press,
long-click, swipe, Back and Home, and independently observed two controlled
button activations, one long-click and one swipe. It reported `OK (1 test)` in
19.713 seconds. On Sony XQ-AT72 (`QV710AF65F`, API 31, arm64-v8a, 4 KiB pages),
AutoJs6 accessibility deliberately remained disabled; a public Python project
instead required `CapabilityUnavailableError` with the exact bounded message
and reported `OK (1 test)` in 0.879 seconds. The physical device's pre-existing
accessibility-service list was byte-for-byte unchanged, no settings UI opened,
and no physical-device gesture success is claimed. Test APK replacement used
`adb install --no-streaming -r -t`; no package was uninstalled and no app data
was cleared.

## Files, Java bridge and isolation

Project Python can read and write its execution-private workspace using normal
Python file APIs, but changes are not written back to the Host project. The
`autojs6.project` API is a separate bounded read-only interface.

`autojs6.files` is an explicit exception to that frozen-copy behavior: it reads
and writes the live Host project root, or the standalone script's Host parent
directory. It accepts only NFC-normalized relative paths (`"."` is the root),
rejects absolute/drive/backslash/control/empty/dot/dot-dot forms, and requires
canonical resolution to stay inside the execution root. Text is strict UTF-8
and at most 32 KiB; writes do not create parents. Direct listings are capped at
128 validated names. No binary, delete, rename, recursive or arbitrary-path API
is declared. A Host write is therefore deliberately visible after execution but
does not appear in the already-frozen Plugin workspace during that execution.

The runtime executes trusted local code and is not a hostile-code sandbox.
Chaquopy's Plugin-local Java bridge may exist, but the Host never sends
`Context`, `ScriptRuntime`, callback sinks or arbitrary Java objects to user
Python. Protocol 1.5 keeps its raw Host Binder in Plugin Kotlin and gives only a
private single-method string bridge to the bootstrap. User-facing modules issue
versioned, bounded pure-data JSON messages through execution-local state.

The U1-R2 output path uses one Plugin-private execution sink with exactly a
stream discriminator and immutable bytes. The object is held only by the
bootstrap capture stream and is never installed in user globals. Each write is
bounded before the sink call, then waits for Host-granted output credit and
ordered callback completion before user execution continues. Cancellation,
timeout, callback death and close wake the wait and reject the in-flight chunk;
the serial callback lane guarantees that an already accepted output callback
precedes the terminal callback and that no output is enqueued after terminal.
This is execution-time transport backpressure, not a new Python capability or
a general Java-object injection surface.

The U1-R2 input path follows the same isolation rule. Its Plugin-private bridge
exposes only one prompt/echo request method and typed reply markers. It contains
no Android `Context`, Binder handle, Host callback or arbitrary Java object,
and is held only by the execution-local replacement for `builtins.input`.

## Explicit results and output artifacts

Protocol 1.4 separates result data from diagnostic output. `autojs6.result.set`
sets at most one strict JSON-compatible value, serializes it deterministically,
and enforces the negotiated UTF-8 byte bound before the terminal document is
created. stdout that happens to contain JSON remains stdout; neither Plugin nor
Host may parse it to manufacture a result.

Calling `autojs6.result.set` is optional. A script which completes without
calling it is a successful execution whose Host result has
`structuredJson == null`; output artifacts remain independently optional. The
Plugin's Chaquopy decoder therefore distinguishes a missing bootstrap field
(an internal contract failure) from a present field whose Python value is
`None`.

`autojs6.artifacts.path` registers one normalized relative logical path and
returns a writable location below the Plugin-private execution result root. The
completed execution must resolve every registered path to a regular non-symlink
file. Count, path, per-file and aggregate byte limits are negotiated in the
request. The Plugin copies each admitted file to a private read-only snapshot,
computes SHA-256, and sends only that snapshot through an exactly referenced
read-only result PFD. The Host requires a regular file, exact declared length,
immediate EOF and matching SHA-256 before exposing Host-owned immutable bytes.

The paired Host now presents a non-null `structuredJson` value in its global
console as `[result] <json>`. It publishes verified artifacts below either the
project root or the single script's parent directory at
`.python-artifacts/execution-<engine-id>-<request-uuid>/` and prints every
absolute path as `[artifact] <path>`. Artifacts are first written into a hidden
same-parent staging directory with their logical paths, lengths and digests
revalidated, then the complete directory is renamed into place. Existing
execution directories are never overwritten. `.python-artifacts` is a reserved
top-level Host output directory and is excluded from later project workspace
snapshots; project entry points inside it are rejected. Publication failure is
reported as `PYTHON_RUNTIME_RESULT_PUBLICATION_FAILED` and cannot turn a
partial directory into a successful result. This is a Host presentation rule,
not a protocol change, and JSON-looking stdout remains diagnostic output.

The artifact protocol is not a general project write-back channel. Failure,
cancellation, timeout, output-limit, callback loss and result rejection publish
neither a JSON result nor artifacts and close/delete all result-owned
descriptors and roots. See
`U1_R2_STRUCTURED_RESULTS_PROTOCOL.md` for the complete wire and ownership
contract. This is still trusted-local execution rather than a hostile-code
sandbox and does not expose Host objects to Python.

## Errors and traceback

- Syntax and runtime failures have one structured terminal result.
- `SystemExit` is a completed bounded exit result.
- Import failures keep their standard Python exception type and bounded text.
- Traceback origins are `project`, `stdlib`, `package` or `generated` and do
  not expose Plugin-private absolute paths.
- Output-limit, cancellation, timeout, Binder death and cleanup remain protocol
  failures with no automatic replay after user code may have started.
- Interactive wait timeout and negotiated input-limit failures use stable
  `INPUT_TIMEOUT`/`INPUT_LIMIT_EXCEEDED` codes in the `INTERACTIVE_INPUT` phase.
- Explicit result or artifact admission failures use
  `OUTPUT_ARTIFACT_REJECTED` in the `RESULT` phase and publish no partial result.

## U1-R0 machine-readable fixture

`tools/tests/fixtures/u1-r0-python-semantics-cases.json` is the executable
subset of this contract. Only cases whose `currentClaim` is
`VERIFIED_PORTABLE` and whose `execution.kind` is `SOURCE` or `PROJECT` execute
in U1-R0. `NONE` cases document current gaps and their target phase without
pretending that a negative absence is runtime acceptance. The current fixture
includes strict UTF-8, finite stdin and nested project-relative import cases
delivered by U1-R1; this remains portable evidence rather than Android
acceptance.

The source gate is:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-u1-r0-python-usability.ps1
```

Its generated report is
`build/reports/python/u1/r0-python-usability-gate.json`. The report must state
that Android compilation, Binder/PFD execution, device verification and public
release were not performed by this gate.
