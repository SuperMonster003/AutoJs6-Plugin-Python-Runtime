******

### Release history

******

# v0.2.0-alpha.1

###### 2026/08/13

* `Hint` Post-0.1 U1 source alpha; live stdin interaction is unavailable and E3 device acceptance remains pending
* `Feature` Add a finite pre-supplied stdin snapshot of at most 1 MiB for deterministic `input()` and `sys.stdin` input and EOF
* `Feature` Complete project import semantics for workspace modules, nested-entry sibling and root modules, and package-relative imports
* `Fix` Decode source as strict UTF-8 before execution so a non-UTF-8 encoding cookie cannot bypass the contract
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
