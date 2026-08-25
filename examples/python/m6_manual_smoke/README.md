# M6 manual Android smoke kit — items 2, 3 and 4

This deterministic kit turns the least obvious parts of the ten-item M6
Android checklist into small self-checking projects. Copy each `m6_*`
directory separately into an AutoJs6 workspace; do not treat this wrapper
directory as one project. Copy the two top-level foreground `.py` files to a
location which AutoJs6 can open in its editor.

The kit does not use the network, install dependencies, change accessibility
or OCR configuration, or clear application data. Before each run, clear the
console or identify the exact `Running [...]` to `finished` interval so output
from an earlier run cannot be mistaken for the current result.

## Item 2 — imports, entry roots and state isolation

1. Run `m6_02_file_entry` as a project. Expect
   `M6-02-FILE-ENTRY-PASS` and a result with `allChecks=true`.
2. Run `m6_02_imports` as a project. Do not run
   `smoke_imports/main.py` directly: its manifest deliberately selects
   `entryMode=module` and `main=smoke_imports.main`.
3. Without restarting Host or Plugin, immediately run `m6_02_imports` again.
4. Both module runs must report `stateCounter=1`, never 2.

Together these projects check file-entry metadata, entry-directory and
project-root imports, package and relative imports, a circular pair,
module-entry metadata, a project-local pure-Python package with transitive
dependency and `.dist-info`, and execution-to-execution module cleanup.

## Item 3 — snapshot, foreground and background input

### 3A snapshot

Run `m6_03a_stdin_snapshot` as a project. No dialog may appear. Expect
`M6-03-SNAPSHOT-PASS` and a result containing:

```json
{"case":"M6-03A","eof":true,"first":"快照值 αβ","rest":"剩余行 Ω\n"}
```

### 3B foreground `input` and `getpass`

Open `m6_03b_foreground_input.py` in the AutoJs6 editor and press Run. Enter
`AUTOJS6-VISIBLE` in the ordinary dialog, then `M6-HIDDEN-7f3a` in the hidden
dialog. Expect `M6-03-FOREGROUND-PASS`, both matched fields true, lengths
15/14, and no occurrence of `M6-HIDDEN-7f3a` in the console.

### 3C scheduled background input

Create a one-shot scheduled task for `m6_03c_background_input`. Do not launch
it manually. The task must show no dialog and promptly print
`M6-03-BACKGROUND-PASS error=EOFError`; its result must contain
`failClosed=true`. Remove or disable the one-shot task afterward.

### 3D optional cancel

Run `m6_03d_foreground_cancel.py` from the editor and press Cancel in the
dialog. Expect `M6-03-CANCEL-PASS` and `error=KeyboardInterrupt`. This path is
extra coverage; 3A, 3B and 3C are the required item-3 slices.

## Item 4 — explicit result, binary artifact and no fabrication

### 4A result and artifact

Run `m6_04a_result_artifact`. Expect exactly one `[result]` and one
`[artifact]` plus:

```text
M6-04-RESULT-ARTIFACT-PASS bytes=34 sha256=2B4A5E4BB7EB7C83D6241C5176D01EEDD31873FA63B28DE10F5553D8FBD25BD4
```

On a connected workstation, pass the absolute `[artifact]` path to:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File .\verify-m6-04-artifact.ps1 `
  -Serial <adb-serial> `
  -DevicePath "/storage/emulated/0/.../m6/expected.bin"
```

The verifier pulls the one file to a random temporary path, checks 34 bytes
and the fixed SHA-256, removes only that local temporary copy, and never
changes the device artifact.

### 4B no explicit result

Clear the console, then run `m6_04b_no_explicit_result`. It deliberately
prints `{"fabricated":true,"source":"stdout-only"}`. The execution must
finish with `M6-04-NO-RESULT-PASS`, but its output interval must contain no
`[result]` and no `[artifact]`.

Report only PASS/FAIL plus any unexpected output. Full release scope and the
other seven items remain defined in
`docs/maintenance/M6_RELEASE_PROCESS.md`.
