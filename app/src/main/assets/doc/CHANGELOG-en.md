******

### Release history

******

# v0.1.0

###### 2026/08/12 (source frozen; not tagged or published)

* `Hint` The 0.1.0 source identity and exact Host lock are frozen; final APK/P3 provenance, official plugin index, tag/Release, and production receipt are pending
* `Feature` Python protocol 1.0-1.1 paired with AutoJs6 6.8.0 / versionCode 5275, a bounded project workspace, and read-only app/device/execution/project capability snapshots
* `Feature` Hot-plug without a host restart: install or re-enable makes the next new execution rediscover and pin identity, while missing or disabled never falls back
* `Feature` In-flight Binder death terminates the current execution without replay; later new executions rediscover the provider
* `Improvement` Fix Chaquopy as a trusted-local, non-sandbox runtime; SM003 is the long-term signer and SuperMonster003 owns runtime, security, and release
* `Dependency` Lock Chaquopy 17.0.0 and CPython 3.13.9; final artifacts require fresh verification after source freeze

# v0.1.0-alpha.1

###### 2026/08/09

* `Hint` R2 proof-of-concept source; Gradle, APK, Binder, and device acceptance have not run
* `Feature` Independent Python protocol V1 provider scaffold with a dedicated runtime process, one active session, and no provider queue
* `Feature` Single-source `__main__` execution, bounded stdout/stderr, structured exceptions, and process-restart cancellation
* `Feature` Fixed-order generation of README files and in-app changelogs in 10 languages
* `Dependency` Preselected Chaquopy 17.0.0 and Python 3.13; packaged versions and dependency hashes still require build verification
