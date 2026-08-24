# Host-queued Python execution

This document describes the M5 concurrent-admission behavior introduced by
AutoJs6 Host commits `afe6f3c73` and `b8cd0d01c`, then integrated into current
Host `master` at `afca7b14c`. It records a current-tree source and offline JVM
contract plus the focused Android acceptance described below. The first device
attempt used an older Host build without that integration and remains recorded
as a useful negative diagnosis; the subsequent `afca7b14c` retest passed.
Publication, true parallel CPython execution, and release qualification are not
claimed.

## Decision

The Runtime Provider continues to admit exactly one active session and keeps
no provider-side queue. Chaquopy owns one process-global CPython interpreter,
execution temporarily replaces process-wide Python state, and authoritative
cancellation retires the whole Plugin process. Running two user executions in
that interpreter at the same time would weaken isolation and cancellation.

Instead, every production Host launch surface converges on one process-local
FIFO admission queue before provider discovery. This is concurrency admission:
multiple AutoJs6 script executions may be submitted together, while their
Python bodies run serially in isolated Plugin process generations.

## Queue contract

- One execution owns the active slot and at most 32 more executions may wait.
  A later submission fails with stable `PYTHON_RUNTIME_BUSY` when all pending
  slots are occupied; existing owners and waiters are not disturbed.
- Admission is FIFO. A new submission cannot barge ahead of an existing
  waiter, including immediately after the active owner releases its slot.
- Waiting happens before source/workspace snapshot creation, Provider binding,
  Binder descriptor ownership, interactive controller creation, and long-task
  foreground-service creation. A queued long task therefore has no premature
  notification or start lease.
- The protocol request timeout starts only after queue admission. The ordinary
  Host engine start time still includes time spent waiting, and an outer Host
  scheduler remains free to stop its queued engine.
- Stopping or destroying a queued engine interrupts its wait, removes exactly
  that waiter, and never opens a Provider session. The next FIFO waiter remains
  eligible. Stopping the active owner retains the existing remote cancel and
  process-restart behavior.
- A `long-running` owner holds the one active slot until it reaches a terminal
  state or its notification Stop action cancels it. Later bounded or long tasks
  wait in the same FIFO queue.

The 32-waiter ceiling bounds Host threads and retained launch state. It is not
advertised as a Plugin capability because neither the protocol nor Provider
behavior changes.

## Runtime-generation handoff

A dispatched session is closed after its terminal callback, which asks the
Plugin to retire that CPython process generation. The Host keeps the service
binding alive for a bounded three-second handoff and waits for Binder process
exit before releasing the FIFO slot. The wait preserves an existing thread
interruption while still completing cleanup.

The Plugin already arms a two-second hard retirement fallback, so the extra
Host interval covers callback drain and Binder death delivery. If Android does
not confirm exit within three seconds, the Host emits a warning and releases
the local slot; the Plugin's authoritative `RETIRING`/single-session gate still
rejects unsafe admission instead of running two sessions.

## Compatibility and exclusions

- Python protocol 1.6, all AIDL methods, Provider metadata, and the three-AAR
  distribution remain byte-for-byte unchanged.
- Old Hosts retain the previous immediate Provider `BUSY` behavior. The queue
  is a Host application feature, not a new Plugin requirement.
- Independent Host launches may queue. `autojs6.engines.run()` still rejects a
  Python child with `NESTED_PYTHON_NOT_ALLOWED`: allowing the current Python
  body to synchronously queue behind itself would deadlock the sole slot.
- This is not simultaneous CPython execution. True parallelism would require
  separately isolated runtime processes or a future interpreter architecture,
  plus independent process-retirement ownership.

## 2026-08-24 first device attempt

On physical device `QV710AF65F`, the user launched `first.py` and immediately
launched `second.py` with AutoJs6 versionCode 5276 and Python Runtime
versionCode 81. The second launch failed at Provider session admission with
`PYTHON_RUNTIME_BUSY: BUSY/SESSION_OPEN`.

That result exactly matches the legacy Host behavior: the installed Host source
did not contain `PythonRuntimeExecutionCoordinator`, so the second execution
reached `PythonRuntimeClient.openSession` instead of waiting before Provider
discovery. It is not evidence that the new FIFO admitted and then failed a
waiter. After this diagnosis, the two queue commits were merged with the current
Host identity-refactor tree and fast-forwarded to Host `master` at `afca7b14c`;
the seven focused Python JVM suites and `assembleAppDebug` pass there.

## 2026-08-24 `afca7b14c` device acceptance

The user installed the exact arm64 Host APK built from `afca7b14c` on
`QV710AF65F` and reported that the complete manual checklist matched the
expected behavior with no issue:

- `second.py` waited behind `first.py` instead of reaching Provider
  `BUSY/SESSION_OPEN`;
- it started automatically only after the first runtime generation completed
  and retired, with the expected fresh Plugin PID;
- stopping `second.py` while it was queued did not disturb `first.py`, and the
  stopped waiter never entered its Python body;
- a later launch still ran normally, proving that queue removal and ownership
  handoff remained healthy.

Only the Host APK was reported as replaced, so this record carries forward the
previously identified Python Runtime versionCode 81. That is sufficient because
protocol 1.6, the AARs, and the Provider binary did not change for Host-side
queuing. This closes the focused M5 concurrent-admission Android smoke; it does
not expand the claim to 32-waiter saturation, a device matrix, publication, or
true parallel CPython.

## Manual smoke

Use `examples/python/m5_concurrency` from the AutoJs6 file explorer:

1. Run `first.py`; it prints its Plugin PID and one tick per second for 15
   seconds.
2. While it is ticking, run `second.py`. It must emit no Python output until
   `first.py` reaches `first finished`.
3. `second.py` then starts automatically and prints its Plugin PID. A fresh PID
   is expected because the first dispatched generation retires before FIFO
   handoff.
4. Repeat, but stop `second.py` while it is queued. The first script must keep
   running, the stopped script must never print `second admitted`, and a later
   new run must still proceed.
5. Optionally run the long-running M5 example first. The bounded second script
   must wait without opening a second foreground notification, then start after
   the notification Stop action retires the long-running generation.

Future device-matrix or release checks should record exact Host and Plugin
commits, APK hashes, API/ABI, and page size independently.
