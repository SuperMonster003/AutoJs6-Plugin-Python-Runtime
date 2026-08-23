# ADR 0001: Python runtime baseline for 0.1.0

- Status: accepted for 0.1.0
- Date: 2026-08-11

## Decision

Use Chaquopy 17.0.0 with its CPython 3.13.9 runtime as the production baseline
for the independently installed Python Runtime Plugin 0.1.0. Package only
`arm64-v8a` and `x86_64`, include the standard library but no third-party Python
packages, start CPython lazily in `:python_runtime`, and retire that process after
each dispatched execution generation.

The release pair is Plugin 0.1.0 with AutoJs6 Host 6.8.0. The minimum compatible
Host is frozen and enforced as versionCode 5275. The final clean Host source is
`2caddcb763b39f0bf450909742fa6ec4caba27a8`; its three-AAR release distribution
manifest SHA-256 is
`9f296ad45c24b7eb3e217e4d0ce6c96ba2593966b2bed1db1f2846d658987818`, as
recorded in `locks/host-api-aars.lock`. Publication state is established by an
independent production receipt; this ADR records the immutable runtime and
source baseline rather than mutable publication status.

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

Containment in `0.1.0` came from an independent Android UID/process, a source
manifest requesting no Android permissions, same-signer and exact-host Binder
admission, bounded Binder/PFD transport, and the absence of an ambient host
capability broker. Starting with `0.2.0`, the plugin intentionally adds the
normal `INTERNET` permission so trusted scripts can use Python's standard-library
network clients. Protocol 1.5 then adds the explicitly allow-listed,
execution-scoped pure-data Host broker decided in ADR 0002. These changes grant
outbound/local-network reachability and the documented Host actions to the
script, but do not enable automatic dependency resolution, online `pip`,
or runtime code downloads. The bootstrap still passes no Android `Context`,
Binder handle, host callback, `ScriptRuntime`, view, or other host object into
Python globals. These controls reduce host exposure but do not turn trusted-local
Python into untrusted-code isolation.

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

## 0.1.0 release identity gates

- Enforce AutoJs6 6.8.0 / versionCode 5275 as the minimum Host and retain the
  exact final clean Host source revision and three-AAR release manifest in the
  Plugin lock.
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
