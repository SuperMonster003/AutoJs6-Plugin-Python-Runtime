# Python execution semantics contract

Status: cumulative U1-R0 through U1-R2 contract plus the first M3 protocol 1.5
Host capability slice. Historical R2 evidence remains covered through E2; the
M1/M2 public Host paths and the focused M3 broker path passed an API 31 /
arm64-v8a / 4 KiB-page physical-device smoke and an API 37 / x86_64 /
16 KiB-page emulator smoke on 2026-08-23. Those smokes are not a release or
device-matrix claim.

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

`0.1.0` is stdlib-only. An absent third-party package raises ordinary
`ModuleNotFoundError`. No import failure may trigger online pip, a runtime
download or another engine. Starting with `0.2.0`, stdlib modules may make
script-initiated network connections because the plugin declares Android's
normal `INTERNET` permission; that permission does not install packages or
fetch code automatically. U1-R3 defines separately signed offline package packs,
pure-Python first and native wheels behind independent ABI gates.

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

These are live Host operations, distinct from the detached launch-time
`app.snapshot()` and `device.snapshot()` data. Every request is bound to the
canonical execution request UUID and a positive monotonic call ID. The Host
also pins the Plugin UID, admits at most 1024 calls, bounds request/response
documents to 64 KiB and text to 32 KiB, and bounds a Host main-thread action to
5 seconds. Calls are serialized by the Python facade and block until a typed
response arrives.

Missing/closed capabilities raise `CapabilityUnavailableError`. Host and wire
failures raise `HostCapabilityError`, whose `code` property is stable. Cleanup
revokes both the private Java bridge and execution-local Python state, including
copied contexts; a call is never replayed after cancellation or connection
loss. The detailed JSON schemas, error codes, lifecycle and exact capability
mapping are in `HOST_CAPABILITY_BROKER_PROTOCOL.md`.

Dynamic device information, direct Host console levels, notifications, files,
dialogs, accessibility, screenshots and OCR remain planned rather than implied
by the generic broker transport.

The focused public Host acceptance invoked the six current method names through
a real protocol 1.5 session on Sony XQ-AT72 (`QV710AF65F`, API 31, arm64-v8a,
4 KiB pages) and an API 37 x86_64 emulator with 16 KiB pages. It verified toast
dispatch, clipboard round-trip and restoration, `False` launch results for
missing targets, a stable `INVALID_ARGUMENT` result for a rejected non-HTTP(S)
URL, strict structured output and private transport cleanup. The runs completed
in 1.607 and 7.183 seconds respectively with `OK (1 test)`; this is focused
current-tree acceptance, not a release claim.

## Files, Java bridge and isolation

Project Python can read and write its execution-private workspace using normal
Python file APIs, but changes are not written back to the Host project. The
`autojs6.project` API is a separate bounded read-only interface.

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
