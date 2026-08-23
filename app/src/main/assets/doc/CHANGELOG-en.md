******

### Release history

******

# v0.3.0-alpha.2

###### 2026/08/23

* `Hint` Second M3 current-tree alpha candidate; the complete first low-risk Host capability slice is implemented, while later capability batches, publication, and a complete device matrix remain outside this claim
* `Feature` Add live `autojs6.device.info()` battery/screen/brightness/volume data, `autojs6.console.log/warn/error` Host console levels, and `autojs6.notice` notifications
* `Improvement` Validate the exact device result schema and return stable `PERMISSION_DENIED` notification errors without opening settings or changing device permission state

# v0.3.0-alpha.1

###### 2026/08/23

* `Hint` First M3 current-tree alpha candidate; protocol 1.5 and the low-risk Host capability slice are implemented, while later capabilities, publication, and a complete device matrix remain outside this claim
* `Feature` Add the protocol 1.5 execution-scoped Host capability broker with pure-data JSON bound to the request UUID, plugin UID, monotonic call IDs, a 1024-call quota, 64 KiB messages, and a 5-second Host dispatch ceiling
* `Feature` Add live `autojs6.toast`, `autojs6.clip.get/set`, and `autojs6.app.launch/launch_app/open_url` Host APIs
* `Improvement` Revoke the broker consistently on terminal, cancellation, Binder death, and cleanup paths, with stable Python mappings for unavailable capabilities and Host or protocol errors

# v0.2.0-alpha.1

###### 2026/08/13

* `Hint` Post-0.1 U1 current-tree alpha candidate; U1-R2 module entry, live output, foreground built-in input, explicit structured JSON, and bounded output artifacts are covered through E2 only; background launches and direct sys.stdin remain non-interactive, R2 E3 remains open, and these current-tree results are not device-matrix, release, or public evidence
* `Feature` Add a finite pre-supplied stdin snapshot of at most 1 MiB for deterministic `input()` and `sys.stdin` input and EOF
* `Feature` Complete project import semantics for workspace modules, nested-entry sibling and root modules, and package-relative imports
* `Feature` Add protocol 1.2 explicit `entryMode=file|module`; module execution uses `runpy` with correct `__package__`, `__spec__`, project-root `sys.path[0]`, and relative imports while file mode remains unchanged
* `Feature` Add protocol 1.3 foreground-only bounded prompt/reply after finite snapshot EOF, with visible echo for built-in `input()` and hidden echo for standard-library `getpass.getpass()`; background launches never open input UI and direct `sys.stdin` stays finite
* `Feature` Add protocol 1.4 explicit strict JSON results and optional output artifacts bounded by count, normalized path, per-file/aggregate size, exact PFD references, and SHA-256, without ever inferring a result from stdout
* `Fix` Decode source as strict UTF-8 before execution so a non-UTF-8 encoding cookie cannot bypass the contract
* `Improvement` Grant `INTERNET` so trusted scripts can use standard-library network clients directly, while online pip and automatic code downloads remain disabled
* `Improvement` Raise the provider execution ceiling to 30 minutes and bounded output to 16 MiB / 16384 chunks
* `Improvement` Move bounded stdout/stderr chunks and credit backpressure into script execution, preserving ordered partial output before terminal and forbidding output afterward
* `Improvement` Use an independent `__main__` per execution and restore stdin/stdout/stderr, argv, cwd, `sys.path`, module, and importer-cache state
* `Improvement` Apply a 5-second lease to an opened session which is never started, then release its inputs, descriptors, and single-session slot
* `Improvement` Enforce minimum Host versionCode 5275 at the Provider Binder boundary instead of relying only on Host-side discovery

# v0.1.0

###### 2026/08/12

* `Hint` Version 0.1.0 freezes the stable Plugin source identity and exact Host 6.8.0/5275 lock
* `Feature` Python protocol 1.0-1.1 paired with AutoJs6 6.8.0 / versionCode 5275, a bounded project workspace, and read-only app/device/execution/project capability snapshots
* `Feature` Hot-plug without a host restart: install or re-enable makes the next new execution rediscover and pin identity, while missing or disabled never falls back
* `Feature` In-flight Binder death terminates the current execution without replay; later new executions rediscover the provider
* `Improvement` Fix Chaquopy as a trusted-local, non-sandbox runtime; SM003 is the long-term signer and SuperMonster003 owns runtime, security, and release
* `Dependency` Lock Chaquopy 17.0.0 and CPython 3.13.9; stable APKs are bound to the final source identity and verified as exact artifacts

# v0.1.0-alpha.1

###### 2026/08/09

* `Hint` R2 proof-of-concept source; Gradle, APK, Binder, and device acceptance have not run
* `Feature` Independent Python protocol V1 provider scaffold with a dedicated runtime process, one active session, and no provider queue
* `Feature` Single-source `__main__` execution, bounded stdout/stderr, structured exceptions, and process-restart cancellation
* `Feature` Fixed-order generation of README files and in-app changelogs in 10 languages
* `Dependency` Preselected Chaquopy 17.0.0 and Python 3.13; packaged versions and dependency hashes still require build verification
