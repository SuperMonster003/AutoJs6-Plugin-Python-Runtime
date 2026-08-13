# Python execution semantics contract

Status: U1-R0 contract for the post-`0.1.0` usability track.

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

A portable result may advance a case only to `VERIFIED_PORTABLE`. Android and
device promotion require the evidence levels defined in `ROADMAP.md`.

## Runtime and source contract

| Property | `0.1.0` historical behavior | Current U1 contract |
| --- | --- | --- |
| Implementation | Chaquopy 17.0.0 / CPython 3.13.9 in the Plugin process | Preserve unless a later release explicitly freezes another identity |
| Script mode | Source bytes compiled as a file-like `__main__` | Preserve file mode; add explicit module mode only in U1-R2 |
| Source encoding | README declared UTF-8, while byte compilation could honor CPython encoding cookies | U1-R1 now accepts strict UTF-8 with optional UTF-8 BOM and rejects NUL, invalid UTF-8 and conflicting non-UTF-8 cookies before dispatch |
| Python grammar | CPython grammar selected by the packaged 3.13 runtime | Ordinary Python 3.13 syntax is supported when its imports/platform dependencies are available |
| Top-level await | Not enabled by ordinary `compile(..., "exec")` | Remains unsupported in file mode; use `asyncio.run()` |
| Python 2 syntax | Unsupported | Remains unsupported |

The Host and Provider must validate the exact SOURCE length and SHA-256. U1-R1
adds strict text admission; it must not silently reinterpret Latin-1 or another
encoding merely because a PEP 263 cookie is present.

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

The bootstrap must restore stdout, stderr, stdin, argv, cwd and `sys.path` on
every terminal path. Project modules and project importer-cache entries must
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

This is finite pre-supplied input. A Host prompt/reply loop which can pause and
request more input is interactive input and belongs to U1-R2.

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
`__spec__` remains `None`. U1-R2 may add a distinct `entryMode=module` backed by
`runpy`; it must not silently replace the current file execution mode.

### Third-party dependencies

`0.1.0` is stdlib-only. An absent third-party package raises ordinary
`ModuleNotFoundError`. No import failure may trigger online pip, a runtime
download or another engine. U1-R3 defines separately signed offline package
packs, pure-Python first and native wheels behind independent ABI gates.

## Files, Java bridge and isolation

Project Python can read and write its execution-private workspace using normal
Python file APIs, but changes are not written back to the Host project. The
`autojs6.project` API is a separate bounded read-only interface.

The runtime executes trusted local code and is not a hostile-code sandbox.
Chaquopy's Plugin-local Java bridge may exist, but the Host never sends
`Context`, `ScriptRuntime`, Binder handles or arbitrary Java objects to Python.
Future Host capabilities use versioned, bounded pure-data messages.

## Errors and traceback

- Syntax and runtime failures have one structured terminal result.
- `SystemExit` is a completed bounded exit result.
- Import failures keep their standard Python exception type and bounded text.
- Traceback origins are `project`, `stdlib`, `package` or `generated` and do
  not expose Plugin-private absolute paths.
- Output-limit, cancellation, timeout, Binder death and cleanup remain protocol
  failures with no automatic replay after user code may have started.

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
