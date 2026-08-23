# U1-R2 foreground interactive input protocol

Status: implemented, with portable/build coverage and current-tree public Host
dialog acceptance against the real Binder/CPython Plugin on one arm64 device
and one 16 KiB-page x86_64 emulator. This is not publication, a complete device
matrix, or stable-release provenance.

## User-visible boundary

Interactive input is deliberately narrower than “live stdin.” A foreground
user-gesture launch may pause the Python built-in `input()` or standard-library
`getpass.getpass()` and display one Host-owned Material dialog. The finite,
verified stdin snapshot is consumed first; the Plugin requests a live reply
only after that snapshot reaches EOF. `input()` requests visible echo, while
`getpass.getpass()` requests hidden echo.

Background launches never receive interactive authority, never open UI, and
retain deterministic finite-input behavior: after the optional snapshot is
exhausted, `input()` raises `EOFError` immediately. Direct
`sys.stdin.read()`, `readline()`, `readlines()`, and `.buffer` access always
refer only to the finite snapshot. They do not become an unbounded callback
stream.

The Host mints an opaque execution grant only in its two explicit foreground
launch paths. The grant contains a weak reference to a live `Activity`; an
absent or arbitrary execution argument cannot forge it. Provider discovery,
background broadcasts, shortcuts, services, timers, and other ordinary launch
paths do not mint the grant. The dialog controller is never sent to the Plugin
or exposed to Python.

## Protocol 1.3 extension

Protocol 1.3 appends the following AIDL methods, preserving all earlier method
order and transaction numbers:

```aidl
IPythonExecutionCallback
    oneway void onInputPrompt(byte[] prompt)

IPythonExecutionSession
    oneway void replyInput(byte[] reply)
```

The tagged-wire extension is:

| Document/field | ID or tag | Compatibility |
| --- | ---: | --- |
| `PythonInteractiveInputPolicy` | `0x50590017` | Nested policy document |
| `PythonInputPrompt` | `0x50590018` | Plugin-to-Host callback |
| `PythonInputReply` | `0x50590019` | Host-to-Plugin session call |
| `supportsInteractiveInput` | capabilities tag 12 | Optional; absent is false |
| input ceilings | resource-limit tags 13–16 | Optional; absent is zero |
| interactive policy | request tag 15 | Required-for-reader when present |

A pre-1.3 reader may ignore the optional capability advertisement. It must
reject a request containing tag 15 instead of silently accepting code whose
input behavior it cannot implement.

The request policy narrows all four Provider ceilings: prompt count, UTF-8
prompt bytes, UTF-8 reply bytes, and reply-wait milliseconds. The Plugin starts
prompt IDs at 1 for each execution and increments exactly once per accepted
prompt. A prompt carries the execution request ID, prompt ID, prompt text,
visible/hidden echo policy, reply byte ceiling, and monotonic timeout. Exactly
one reply with the same request and prompt IDs is accepted. Reply status is one
of `VALUE`, `EOF`, or `CANCELLED`; `VALUE` requires text and permits an empty
string, while the other statuses forbid text.

The current Provider advertises these narrower operational limits:

- prompt: 4 KiB UTF-8;
- reply: 64 KiB UTF-8;
- prompts: 128 per execution;
- reply wait: 60 seconds, additionally narrowed by the execution timeout.

The protocol-wide hard ceilings remain 16 KiB, 64 KiB, 1,024 prompts, and 30
minutes respectively.

## Bootstrap and bridge isolation

The Plugin creates one private `ChaquopyInputBridge` for an authorized
execution and temporarily replaces `builtins.input` and `getpass.getpass`. The bridge has one
reflective method carrying prompt text and a fixed echo token. It validates the
typed reply and returns a private status marker to the bootstrap; it is not put
in user globals and contains no Android `Context`, Binder handle, Host callback,
or arbitrary capability object.

The patched built-in writes the prompt to captured stdout exactly once; patched
`getpass.getpass()` writes it to the explicit stream or captured stderr. Both
read one line from the finite snapshot first and request a live reply only on
EOF. `VALUE` returns text, `EOF` raises `EOFError`, and `CANCELLED` raises
`KeyboardInterrupt`. The original callables and all stdio/process state are
restored on every terminal path. Bridge delivery, timeout and negotiated limit
failures are rethrown to the Kotlin session so they cannot be mistaken for an
ordinary Python exception.

## Wait and terminal lifecycle

Only one prompt may be pending. The Provider waits on the same session signal
used by output credit and lifecycle transitions. Every one of these paths
clears the pending prompt and wakes the wait:

- explicit session cancellation;
- the execution deadline;
- admission or execution callback Binder death;
- Host close or service destruction;
- callback-delivery failure and hard retirement;
- runtime-generation retirement after cancellation/timeout.

The worker also receives an interrupt during close/retirement. A duplicate,
unsolicited, out-of-order, wrong-request, wrong-prompt, or oversized reply
fails closed and retires a dispatched generation. Once terminal or closed, a
late reply is ignored and can never revive the execution.

The Host owns a separate single-thread, queue-one input lane so its script
thread and Binder callbacks never block on dialog interaction. Cancellation,
timeout, connection loss, Plugin state change, engine destruction, or any
terminal callback interrupts that task and dismisses the active dialog.

## Evidence boundary

Portable tests cover snapshot-first behavior, multiple live prompts, visible
`input()`, hidden `getpass.getpass()`, empty values, EOF, cancellation, bounded
direct `sys.stdin`, and restoration.
Plugin JVM tests cover bridge markers and exact failure propagation. Shared API
tests freeze AIDL and tagged-wire goldens, old-reader compatibility, all
limits, and the monotonic one-shot prompt state machine. Host JVM tests cover
unforgeable/missing authority, Provider selection, and interactive request
planning. The public Android test additionally follows the exact foreground
methods used by the editor and Explorer, submits replies through the real
Host-owned dialogs, asserts the visible/password accessibility distinction,
and reaches real CPython structured results without logging reply text. It
passed on Sony XQ-AT72 (`QV710AF65F`, API 31, arm64-v8a, 4 KiB pages) in
2.232 seconds and an API 37 x86_64 emulator with 16 KiB pages in 8.853 seconds.

The reproducible partial gate is:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-u1-r2-interactive-input.ps1 -HostRepository D:\idea-projects\AutoJs6
```

Its report is
`build/reports/python/u1/r2-interactive-input-contract.json`. It must remain
`phaseStatus=PARTIAL` and `r2Complete=false`; this scope-specific report does
not retroactively claim result transport or device evidence. Protocol 1.4
structured JSON/output artifacts are now covered independently by
`U1_R2_STRUCTURED_RESULTS_PROTOCOL.md` and its partial E2 report. The dedicated
five-selector E3 runner/verifier boundary is documented in
`U1_R2_DEVICE_EVIDENCE.md`; the focused M2 smoke above is deliberately not a
claim that this legacy canonical transaction, publication, or release
provenance was completed. The paired Host test is commit `70ea17097`.
