# U1-R2 explicit module-entry protocol

Status: implemented and covered through E2 on the current Host and Plugin
trees. This document does not claim Android Binder/device evidence or stable
release provenance.

## User and Host selection

The Host execution configuration key is `autojs6.python.entryMode`. Its only
accepted string values are `file` and `module`; an absent value selects `file`.
No spelling, case, numeric, Boolean, or implicit-source heuristic is accepted.
An invalid value fails with the stable Host code
`PYTHON_RUNTIME_ENTRY_MODE_INVALID` before provider dispatch.

Module mode is valid only for an explicitly admitted Python project. Given the
project entry file `pkg/main.py`, the Host derives the wire entry point
`pkg.main`. A standalone source remains file mode and never acquires an
implicit parent-directory workspace.

## Protocol 1.2 wire extension

Protocol 1.2 appends two default-false/default-file fields without changing the
V1 AIDL surface:

| Schema | Tag | Type | Meaning |
| --- | ---: | --- | --- |
| Capabilities (`0x50590002`) | 11 | optional `BOOLEAN` | `supportsModuleEntry`; absent means false |
| Execution request (`0x50590010`) | 14 | optional `INT32` | entry mode; absent means file (`1`), module is `2` |

The Host omits request tag 14 for file mode, preserving the protocol 1.0/1.1
file-request bytes and decode behavior. For module mode it emits tag 14 with
the wire field's required-for-reader flag. A reader which does not know tag 14
therefore rejects that request as an unknown required field instead of
silently interpreting the dotted entry point as a file path.

The shared validation contract enforces all of the following:

- module capability requires workspace-archive capability and a runtime range
  which reaches protocol 1.2;
- a module request requires a negotiated protocol of at least 1.2, a workspace
  descriptor, and a provider which advertises module entry;
- a dotted module name is NFC-normalized and within the entry-point byte
  ceiling, and every segment is an ASCII Python identifier which is not a hard
  keyword;
- `__init__` is rejected as the final segment, avoiding an ambiguous mapping
  between a package and a source module;
- the source uses an exact lowercase `.py` extension and no directory or file
  stem contains a literal dot, preventing two different file layouts from
  collapsing to the same dotted name;
- mapping is reversible and deterministic: `pkg/main.py` maps to `pkg.main`,
  and `pkg.main` maps to `pkg/main.py`.

These rules are shared by Host planning and Plugin validation rather than
being inferred independently from enum names or string replacement at the
execution boundary.

## Plugin staging and execution

The workspace continues to be admitted, bounded, normalized, extracted, and
owned under the existing project-snapshot rules. Module mode then maps its
dotted entry to the staged `.py` file and verifies that the file bytes exactly
match the separately hashed SOURCE descriptor. A mismatch fails before user
code starts.

File mode retains the existing compile/exec path, logical `__file__` and
`sys.argv[0]`, `__spec__ is None`, entry-directory-first import order, and
project-root fallback.

Module mode instead prepends only the project root and calls:

```python
runpy.run_module(entry_point, run_name="__main__", alter_sys=True)
```

This gives standard module behavior for `__package__`, `__spec__`,
`__file__`, `sys.argv[0]`, and package-relative imports. Output remains on the
same execution-time bounded sink. Before `run_module`, the Plugin temporarily
evicts the target top-level namespace from `sys.modules`, resolves the module
again with the private project root first, and requires the spec origin to be
the exact staged entry file. The original namespace is restored afterward, so
an already imported stdlib/package name cannot redirect the requested project
entry. All modes restore stdin/stdout/stderr,
`sys.argv`, cwd, `sys.path`, importer cache, `sys.modules`, and execution
context on every terminal path. Structured traceback paths are converted back
to logical project-relative names and do not expose the private workspace.

## Evidence boundary

The portable bootstrap suite distinguishes file and module metadata/import
behavior, rejects source mismatch and unknown modes before user code, verifies
traceback sanitization, and checks module/cache cleanup. JVM tests cover
protocol constants, default decoding, golden bytes, unknown-reader fail-closed
behavior, validation/mapping, Host planning/provider selection, workspace
materialization, and advertised Plugin capability.

The reproducible partial gate is:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-u1-r2-module-io.ps1 -HostRepository D:\idea-projects\AutoJs6
```

Its report is `build/reports/python/u1/r2-module-io-contract.json`. That
scope-specific report remains `phaseStatus=PARTIAL` and `r2Complete=false` and
does not retroactively claim result transport or device evidence. Foreground
prompt/reply input and protocol 1.4 structured JSON/output artifacts are covered
independently by `U1_R2_INTERACTIVE_INPUT_PROTOCOL.md` and
`U1_R2_STRUCTURED_RESULTS_PROTOCOL.md`, each with its own partial E2 report.
R2 E3 remains open. Its dedicated five-selector exact-artifact tooling and
operator boundary are documented in `U1_R2_DEVICE_EVIDENCE.md`; preparing those
tools or compiling AndroidTest sources is not a device run. A dirty
Host-generated AAR triplet is development input only and cannot establish
stable release provenance.
