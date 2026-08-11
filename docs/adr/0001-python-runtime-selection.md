# ADR 0001: Python runtime baseline for 0.1.0

- Status: accepted for 0.1.0 release preparation
- Date: 2026-08-11

## Decision

Use Chaquopy 17.0.0 with its CPython 3.13.9 runtime as the production baseline
for the independently installed Python Runtime Plugin 0.1.0. Package only
`arm64-v8a` and `x86_64`, include the standard library but no third-party Python
packages, start CPython lazily in `:python_runtime`, and retire that process after
each dispatched execution generation.

The intended release pair is Plugin 0.1.0 with AutoJs6 Host 6.8.0. The exact
final Host identity (version name/code, source revision, release-AAR manifest and
the corresponding compatibility bounds) is still a release blocker and must be
frozen before final artifacts are built. This ADR does not claim that a final
Host 6.8.0 pair, a `v0.1.0` tag, or a published release already exists.

## Why this runtime

- Chaquopy 17 documents minSdk 24 and Android Gradle Plugin 7.3 through 9.2
  support.
- Its Python 3.13 runtime matches the project's 64-bit-only initial ABI scope.
- It supplies maintained Android packaging and interpreter startup while the
  plugin owns the Binder, descriptor, execution, output and process-lifecycle
  contract.
- Version 17 reports 16 KB page support for Chaquopy itself. Bundled third-party
  wheels would require separate verification, so 0.1.0 bundles none.

An official-CPython Android embedding comparison remains useful future research,
but it is not a 0.1.0 release gate. Replacing Chaquopy would be a new runtime
decision with fresh protocol, packaging, security and device evidence.

## Trusted-local, non-sandbox boundary

Python input is user-selected local code trusted for the permissions and APIs
reachable by the plugin UID. Chaquopy exposes a `java` module and `jclass`;
disabling a convenience import hook does not create a Java-interoperability
security boundary. The plugin therefore does **not** claim to sandbox hostile
Python.

Containment comes from an independent Android UID/process, a source manifest
requesting no Android permissions, same-signer and exact-host Binder admission,
bounded Binder/PFD transport, and the absence of an ambient host capability
broker. The bootstrap passes no Android `Context`, Binder handle, host callback,
`ScriptRuntime`, view, or other host object into Python globals. These controls
reduce host exposure but do not turn trusted-local Python into untrusted-code
isolation.

## Cancellation, hot-plug and generation policy

Chaquopy exposes one process-wide Python singleton. Java thread interruption,
Python tracing and asynchronous exception injection cannot reliably stop native
extensions or hostile code. The provider therefore advertises
`PROCESS_RESTART_ONLY`, not cooperative cancellation.

A normal result or structured Python failure is delivered first; the host then
closes the session and the plugin retires `:python_runtime`. Cancel, timeout,
callback death or Binder death terminates the current execution generation. A
request which reached dispatch is never replayed automatically.

Provider availability is hot-plugged without a Host restart:

- installing or re-enabling the plugin makes the next new execution eligible;
- a missing or disabled provider must produce an install/enable prompt and must
  never fall back to another script engine;
- uninstall, disable or update during an in-flight call may kill its Binder, in
  which case that execution terminates and is not replayed; and
- a later new execution performs discovery again, validates the selected
  component and pins its current package/signing/runtime identity.

## 0.1.0 release-preparation gates

- Freeze and enforce the exact final AutoJs6 6.8.0 Host identity and release-AAR
  manifest used by the plugin.
- Keep every Chaquopy/CPython artifact, Gradle wrapper byte, dependency checksum
  and packaged ABI/native inventory pinned and independently reviewable.
- Confirm packaged `platform.python_version()` is exactly 3.13.9 and retain
  focused Binder/PFD/UID/death, cancellation/rebind and no-replay evidence on
  the exact final artifacts.
- Sign with the long-term SM003 release identity recorded in
  `locks/release-identity.lock`; any signer rotation requires an explicit new
  trust decision.
- Generate fresh source, build, focused device and publication evidence after
  every source, lock, AAR, version or signer change. Historical RC evidence must
  not be relabeled as stable-release evidence.

## Official references

- https://chaquo.com/chaquopy/doc/current/android.html
- https://chaquo.com/chaquopy/doc/current/changelog.html
- https://chaquo.com/chaquopy/doc/current/python.html
- https://docs.python.org/3/using/android.html
