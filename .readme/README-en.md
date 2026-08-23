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
- Accept a finite pre-supplied stdin snapshot of at most 1 MiB; after it reaches EOF, an explicit foreground launch may continue the built-in `input()` through bounded protocol 1.3 prompt/reply, while standard-library `getpass.getpass()` uses hidden echo.
- Select explicit `entryMode=file|module` for an admitted project; module mode uses standard `runpy` metadata, project-root `sys.path[0]`, and package-relative imports while file mode keeps ordinary script semantics.
- Deliver bounded stdout/stderr chunks in their original order during script execution; exhausted credits backpressure execution.
- Set an explicit strict JSON result of at most 64 KiB and transfer up to 16 optional output artifacts under protocol 1.4 path, size, and SHA-256 limits; never infer a result from stdout.
- Call live `toast`, `clip.get/set`, `app.launch/launch_app/open_url`, `device.info`, `console.log/warn/error`, and permission-aware `notice` operations through the execution-scoped pure-data protocol 1.5 broker, which is revoked at terminal.
- Report `SystemExit`, syntax errors, and runtime exceptions with a bounded structured traceback.
- Allow one active session in the runtime process with no provider-side queue.
- Require no host restart: the next new execution after install or re-enable rediscovers and pins the provider, while in-flight Binder death terminates that execution and is never automatically replayed.

******

### Runtime and data formats

******

Protocol V1 currently declares the following scope:

```text
input: UTF-8 Python source snapshot
output: ordered bounded stdout/stderr chunks, explicit strict JSON, and SHA-256-manifested output artifacts
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
protocol: 1.0-1.5
```

The plugin accepts an independent SOURCE, an optional bounded workspace archive, a finite pre-supplied stdin snapshot of at most 1 MiB, and the protocol 1.1 read-only host capability snapshot. Protocol 1.2 adds explicit file/module entry negotiation for admitted projects. Protocol 1.3 adds Host-owned, foreground-only prompt/reply for the built-in `input()` after snapshot EOF; standard-library `getpass.getpass()` uses hidden echo. Protocol 1.4 adds explicit strict JSON and optional SHA-256-manifested output artifacts; stdout remains diagnostic text and is never parsed as a result. Protocol 1.5 adds a pure-data Host capability broker bound to one execution, the plugin UID, call order, and a finite quota. Direct `sys.stdin` remains finite, background launches never open input UI, and user scripts receive no Context, raw Binder, host runtime object, or callback sink.

******

### Host integration status

******

> Version 0.1.0 is paired only with AutoJs6 6.8.0, with minimum Host versionCode 5275 frozen and enforced; the final clean Host source revision and three-AAR distribution manifest are recorded in the lock. Each new execution rediscovers the provider; missing or disabled states prompt install or enable and never fall back, while install or re-enable needs no Host restart. Stable APK identity is bound to that exact Plugin source and Host lock.

```text
release target: 0.3.0-alpha.2
release state: 0.3.0-alpha.2 current-tree candidate; M1 and M2 are complete, and the complete first low-risk protocol 1.5 Host capability slice passed the public engine path on an API 31 arm64 device and an API 37 x86_64 16 KiB-page emulator; later M3 batches, a complete device matrix, publication, and release evidence remain outside this claim
paired host: AutoJs6 6.8.0 / current acceptance versionCode 5276 / minimum versionCode 5275
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

- Source is capped at 4 MiB, total output at 16 MiB, each output chunk at 16 KiB, and output count at 16384 chunks.
- Request timeout is capped at 30 min, with one active session per process and no provider-side queue.
- SOURCE descriptors adopt complete Binder receiver-side PFD ownership, preserve reliable-pipe error channels, and close at terminal or session close.
- Output is delivered chunk by chunk under credits during execution; exhausted credits pause the script, accepted output precedes the single terminal, and output after terminal is forbidden.
- Structured JSON is capped at 64 KiB; at most 16 artifacts are accepted with 1024 UTF-8 bytes paths, 4 MiB per file, 8 MiB aggregate, and Host verification of exact length, EOF, and SHA-256.
- Protocol 1.5 admits at most 1024 Host calls per execution, caps each request/response at 64 KiB and text at 32 KiB, and waits at most 5 s for one Host dispatch.
- Cancellation uses process restart rather than CPython-level cooperation; native extensions and blocking calls still require later Android validation.
- The plugin grants `INTERNET` for script-initiated standard-library networking; online pip, automatic code downloads, and runtime third-party package installation remain unsupported.

******

### Undeclared capabilities

******

- General live stdin and direct `sys.stdin` callback streaming are unavailable. Foreground interaction applies only to built-in `input()` and standard-library `getpass.getpass()` after the finite snapshot of at most 1 MiB reaches EOF. Workspace write-back, online pip, and runtime wheel downloads remain unsupported.
- There is no UI scripting, debugger, REPL, or arbitrary access to host Java objects.
- The live broker covers the complete first low-risk slice; files, dialogs, accessibility, screenshot, and OCR APIs remain undeclared.
- 32-bit Android support is not declared, and arbitrary third-party native wheels are not guaranteed.
- The current tree has API 31 arm64-v8a device smoke evidence and API 37 x86_64 16 KB-page emulator smoke evidence; neither is presented as a complete device matrix or release qualification.

******

### Roadmap

******

The R6-P2/P3 local RC and concentrated device evidence remain historical. This clean VERSION_BUILD=11 freeze commit fixes the stable Plugin source identity and exact Host 6.8.0/5275 lock; stable APK provenance is evaluated against those exact identities, and any production receipt must use the same basis. A full API-by-ABI matrix and a new soak are not automatic gates.

- [View ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

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

The runtime locks Chaquopy 17.0.0 and CPython 3.13.9 from Maven and packages only the stdlib. The release gate checks dependency metadata, native libraries, notices, the SM003 signer, and all three distribution APKs against the exact identity. A focused current-tree API 37 x86_64 16 KB-page emulator smoke has passed; this is not a comprehensive compatibility gate or device-matrix claim.

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
