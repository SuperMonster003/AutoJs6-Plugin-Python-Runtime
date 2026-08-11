# ADR 0001: R2 Python runtime candidate

- Status: provisional for the R2 proof of concept
- Date: 2026-08-09

## Decision

Use Chaquopy 17.0.0 with its Python 3.13 line (expected CPython 3.13.9) for the first
independent-APK execution proof. Package only arm64-v8a and x86_64, install no pip
requirements, start CPython lazily inside :python_runtime, and retire that process after
every dispatched execution generation.

This is a POC selection, not the final production-runtime decision. Before promotion, an
official CPython Android embedding POC must be measured against the same protocol and device
matrix.

## Why this candidate

- Chaquopy 17 documents minSdk 24 and Android Gradle Plugin 7.3 through 9.2 support.
- Its Python 3.13 runtime matches the project's 64-bit-only initial ABI scope.
- It supplies Android packaging and interpreter startup so R2 can concentrate on the Binder,
  descriptor, execution, output, and process-lifecycle contract.
- Version 17 reports 16 KB page support for Chaquopy itself, while also warning that bundled
  third-party wheels require separate verification. R2 bundles no third-party wheels.

## Non-sandbox boundary

Chaquopy exposes a java module and jclass. Disabling its convenience import hook does not
constitute a secure Java-interoperability boundary. The POC therefore does not claim to sandbox
Python. Its intended containment is the independent Android UID/process, a source manifest which
requests no Android permissions, a same-signer Binder caller policy, and the absence of any host
capability broker. The merged APK permission set must still be verified before acceptance.

The bootstrap deliberately passes no Context, Binder, host callback, ScriptRuntime, View, or
other host object into user globals. That narrower property remains useful even though Python can
reach Java APIs available inside the plugin process.

## Cancellation and generation policy

Chaquopy exposes one process-wide Python singleton. Java thread interruption, Python tracing, and
asynchronous exception injection do not reliably stop native extensions or hostile code. R2 thus
advertises PROCESS_RESTART_ONLY and not cooperative cancellation.

A normal result or structured Python failure is delivered first; the host then closes the session
and the plugin retires :python_runtime. Cancel, timeout, or callback death retires it immediately.
The host interprets Binder death using its local cancel/deadline state and must never replay a
dispatched request. A new bind creates a new positive runtime generation.

## Promotion blockers

- Produce and compare an official CPython Android embedding POC.
- Resolve and hash every Chaquopy/CPython artifact and record dependency verification metadata.
- Revalidate the checked-in Gradle 9.5.0 wrapper JAR against its official
  distribution checksum, wrapper-main container hash and embedded-entry hash
  after any wrapper or distribution change; the URL alone does not establish
  wrapper-JAR provenance.
- Confirm packaged platform.python_version() is exactly 3.13.9.
- Verify every packaged ELF for both declared ABIs and 16 KB page compatibility.
- Compile and run Binder/PFD/UID/death, cancellation/rebind, no-replay, and leak tests.
- Decide whether Chaquopy's Java bridge is acceptable for production or whether official CPython
  embedding is required to narrow the plugin-local attack surface.

## Official references

- https://chaquo.com/chaquopy/doc/current/android.html
- https://chaquo.com/chaquopy/doc/current/changelog.html
- https://chaquo.com/chaquopy/doc/current/python.html
- https://docs.python.org/3/using/android.html
