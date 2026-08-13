<!--suppress HtmlDeprecatedAttribute, HttpUrlsUsage -->

<div align="center">
  <p>Independent Python runtime plugin. Execute Python scripts in a dedicated plugin process</p>

  <p>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/releases"><img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/SuperMonster003/AutoJs6-Plugin-Python-Runtime?label=Release"/></a>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/issues"><img alt="GitHub closed issues" src="https://img.shields.io/github/issues/SuperMonster003/AutoJs6-Plugin-Python-Runtime?color=A24232&label=Issues"/></a>
    <a href="https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/LICENSE"><img alt="GitHub License" src="https://img.shields.io/github/license/SuperMonster003/AutoJs6-Plugin-Python-Runtime?color=534BAE&label=License"/></a>
  </p>
</div>

******

### Languages

******

The current README.md supports the following languages:

- [简体中文 [zh-Hans]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-zh-Hans.md)
- [繁體中文 (香港) [zh-Hant-HK]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-zh-Hant-HK.md)
- [繁體中文 (台灣) [zh-Hant-TW]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-zh-Hant-TW.md)
- English [en] # current
- [Français [fr]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-fr.md)
- [Español [es]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-es.md)
- [日本語 [ja]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-ja.md)
- [한국어 [ko]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-ko.md)
- [Русский [ru]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-ru.md)
- [العربية [ar]](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/.readme/README-ar.md)

******

### Introduction

******

Python Runtime is an independent provider for version 1 of the Python protocol. The host gives one Python source snapshot to a dedicated plugin process, which executes it with CPython and returns bounded output, structured exceptions, and exactly one terminal state.

> The 0.1.0 source identity and exact Host lock are frozen. Existing local RC build, APK, Binder, and one API 31 arm64-v8a device evidence remain historical; stable APK/P3 provenance is bound to the exact release identity, while a production receipt is a separate post-publication evidence level.

******

### Features

******

- Execute one UTF-8 Python source snapshot as `__main__`.
- Accept a finite pre-supplied stdin snapshot of at most 1 MiB for `input()`; no live prompt/reply interaction is provided.
- Collect stdout and stderr in their original order, then deliver bounded chunks under credits.
- Report `SystemExit`, syntax errors, and runtime exceptions with a bounded structured traceback.
- Allow one active session in the runtime process with no provider-side queue.
- Require no host restart: the next new execution after install or re-enable rediscovers and pins the provider, while in-flight Binder death terminates that execution and is never automatically replayed.

******

### Runtime and data formats

******

Protocol V1 currently declares the following scope:

```text
input: UTF-8 Python source snapshot
output: ordered bounded stdout/stderr chunks and a structured terminal result
runtime: Chaquopy 17.0.0
Python request: 3.13
expected packaged Python: 3.13.9
```

The build requests Python 3.13. Frozen local RC artifacts and exact device execution recorded CPython 3.13.9; the final 0.1.0 version and hashes must still be rechecked after source freeze.

******

### Plugin interface

******

The host discovers and calls the plugin with the following identities:

```text
service action: org.autojs.plugin.python.RUNTIME
official index plugin id: python-runtime
official index engine: python
official index variant: cpython-3.13
protocol provider id: org.autojs.python.runtime.cpython
engine: python
protocol: 1.0-1.1
```

The plugin accepts an independent SOURCE, an optional bounded workspace archive, a finite pre-supplied stdin snapshot of at most 1 MiB, and the protocol 1.1 read-only host capability snapshot. Stdin is not a live interaction channel; no Context, Binder, host runtime object, or callback sink is injected into script globals.

******

### Host integration status

******

> Version 0.1.0 is paired only with AutoJs6 6.8.0, with minimum Host versionCode 5275 frozen and enforced; the final clean Host source revision and three-AAR distribution manifest are recorded in the lock. Each new execution rediscovers the provider; missing or disabled states prompt install or enable and never fall back, while install or re-enable needs no Host restart. Stable APK identity is bound to that exact Plugin source and Host lock.

```text
release target: 0.2.0-alpha.1
release state: post-0.1 U1 clean-source alpha candidate; live stdin interaction is unavailable; U1-R1 E3 exists only when a matching canonical PASS report binds the exact Host/Plugin artifacts tested on QV710AF65F/API 31/arm64; it is not published and does not establish device-matrix, release, or public evidence; prior 0.1.0 artifacts do not cover U1
paired host: AutoJs6 6.8.0 / versionCode 5275
release branch: master
long-term signer: SM003
runtime/security/release owner: SuperMonster003
```

******

### Security and privacy

******

The Chaquopy runtime is for trusted local scripts, not a hostile-code sandbox. The exported service requires the host signature permission and rechecks UID, package, and signer; a separate Android UID, dedicated process, and narrow Binder boundary reduce host exposure but do not sandbox Python. SM003 is the long-term release signer, and SuperMonster003 owns runtime, security, and release.

******

### Operational limits

******

- Source is capped at 4 MiB, total output at 4 MiB, each output chunk at 16 KiB, and output count at 4096 chunks.
- Request timeout is capped at 60 s, with one active session per process and no provider-side queue.
- SOURCE descriptors adopt complete Binder receiver-side PFD ownership, preserve reliable-pipe error channels, and close at terminal or session close.
- Output is currently bounded in plugin memory before credit-backed delivery; execution-time streaming backpressure is not claimed.
- Cancellation uses process restart rather than CPython-level cooperation; native extensions and blocking calls still require later Android validation.
- The stdlib-only policy forbids online pip and third-party Python packages. The merged APK permission set remains a build-gate check.

******

### Undeclared capabilities

******

- Live interactive stdin is unavailable; only a finite pre-supplied snapshot of at most 1 MiB is supported. Workspace write-back, online pip, and runtime wheel downloads remain unsupported.
- There is no UI scripting, debugger, REPL, or arbitrary access to host Java objects.
- There is no live AutoJs6 capability broker; the first APIs use only the app/device/execution/project snapshot frozen at execution start and bounded read-only access to the plugin-private workspace.
- 32-bit Android support is not declared, and arbitrary third-party native wheels are not guaranteed.
- arm64-v8a has API 31 device evidence; x86_64 currently has packaging evidence only and is not presented as device execution or a complete device matrix.

******

### Roadmap

******

The R6-P2/P3 local RC and concentrated device evidence remain historical. This clean VERSION_BUILD=11 freeze commit fixes the stable Plugin source identity and exact Host 6.8.0/5275 lock; stable APK provenance is evaluated against those exact identities, and any production receipt must use the same basis. A full API-by-ABI matrix and a new soak are not automatic gates.

- [View ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### Release history

******

# v0.2.0-alpha.1

###### 2026/08/13

* `Hint` Post-0.1 U1 clean-source alpha candidate; live stdin interaction is unavailable, and U1-R1 E3 is represented only by a matching canonical PASS report for the exact Host/Plugin artifacts on QV710AF65F/API 31/arm64; this is not device-matrix, release, or public evidence
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

##### For more releases

* [CHANGELOG-en.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/app/src/main/assets/doc/CHANGELOG-en.md)

******

### Verification

******

Filesystem-only static verification which invokes neither Gradle nor ADB:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-r6-release-source.ps1
```

Portable bootstrap semantic tests under the machine's local CPython:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B -m unittest tools.tests.test_bootstrap -v
```

Static and local CPython checks cannot replace Android evidence. Existing local RC and single-device results are historical; release acceptance uses build, APK, Binder, and representative-device checks directly bound to the exact release identity.

******

### Build

******

Documentation generation itself runs no build. Release configuration fails closed on protocol AAR, SHA-256, signer, or runtime-lock drift; stable artifacts are accepted only when bound to the exact release identity.

The following release AARs must be staged and locked in the repository `libs` directory before a build:

```text
common-plugin-api.aar
protocol-wire-api.aar
python-runtime-api.aar
```

The runtime locks Chaquopy 17.0.0 and CPython 3.13.9 from Maven and packages only the stdlib. The release gate checks dependency metadata, native libraries, notices, the SM003 signer, and all three distribution APKs against the exact identity; 16 KB page compatibility currently has no dedicated gate and is not claimed as verified.

******

### License

******

Project source is licensed under MPL-2.0. Chaquopy, CPython, and other third-party components retain their licenses; attribution and upstream and project-source access are documented in `THIRD_PARTY_NOTICES.md`.

******

### Resource layout

******

```text
.readme/lang_*.json
.changelog/lang_*.json
.python/generate_markdown.py
app/src/main/assets/doc/CHANGELOG-*.md
app/src/main/res/values-*/strings.xml
```

`.python/generate_markdown.py` generates README files and in-app changelogs in 10 languages from fixed-order JSON sources. Android strings are maintained in their own resource directories.

******

### Links

******

- AutoJs6 documentation: https://docs.autojs6.com
- Chaquopy: https://chaquo.com/chaquopy/
- Python: https://www.python.org/
