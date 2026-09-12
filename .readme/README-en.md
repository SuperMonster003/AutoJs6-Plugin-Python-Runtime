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
- Import project-local pure-Python packages and `.dist-info` metadata from the admitted project root without online pip or runtime installation.
- Deliver bounded stdout/stderr chunks in their original order during script execution; exhausted credits backpressure execution.
- Set an explicit strict JSON result of at most 64 KiB and transfer up to 16 optional output artifacts under protocol 1.4 path, size, and SHA-256 limits; never infer a result from stdout.
- Call live `toast`, `clip.get/set`, `app.launch/launch_app/open_url`, `device.info`, `console.log/warn/error`, permission-aware `notice`, bounded `files.read_text/write_text/exists/is_file/is_dir/list`, foreground-only `dialogs.alert/confirm/prompt/select`, `engines.current/run/stop_self`, bounded `automator.click/long_click/press/swipe/back/home`, bounded `selector.snapshot/find/click/set_text`, `images.capture_screen`, `images.find_color`, `images.find_image`, and `ocr.recognize` operations through the execution-scoped pure-data protocol 1.5 broker, which is revoked at terminal.
- Protocol 1.6 adds explicit `long-running` projects through `executionMode=long-running`, with no elapsed deadline, a Host foreground notification and Stop action, and ordered Provider heartbeats every 15 s; background launch surfaces fail closed and never downgrade the request.
- The paired Host admits concurrent Python launches through a fair FIFO before Provider discovery: one active owner and at most 32 waiters; queued Stop is interruptible and a dispatched generation waits up to 3 s for Binder exit before handoff, while the Provider remains single-session with no queue.
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
protocol: 1.0-1.6
```

The plugin accepts an independent SOURCE, an optional bounded workspace archive, a finite pre-supplied stdin snapshot of at most 1 MiB, and the protocol 1.1 read-only host capability snapshot. Protocol 1.2 adds explicit file/module entry negotiation for admitted projects. Protocol 1.3 adds Host-owned, foreground-only prompt/reply for the built-in `input()` after snapshot EOF; standard-library `getpass.getpass()` uses hidden echo. Protocol 1.4 adds explicit strict JSON and optional SHA-256-manifested output artifacts; stdout remains diagnostic text and is never parsed as a result. Protocol 1.5 adds a pure-data Host capability broker bound to one execution, the plugin UID, call order, and a finite quota. Protocol 1.6 adds explicit `long-running` execution with ordered liveness heartbeats, a Host-owned foreground service, and manual Stop; background surfaces are rejected without downgrade. Foreground Host dialogs require the same live Activity-backed authorization; background launches receive `INTERACTIVE_NOT_ALLOWED` without opening UI. Direct `sys.stdin` remains finite, background launches never open input UI, and user scripts receive no Context, raw Binder, host runtime object, or callback sink.

******

### Host integration status

******

> Version 0.1.0 is paired only with AutoJs6 6.8.0, with minimum Host versionCode 5275 frozen and enforced; the final clean Host source revision and three-AAR distribution manifest are recorded in the lock. Each new execution rediscovers the provider; missing or disabled states prompt install or enable and never fall back, while install or re-enable needs no Host restart. Version 0.5.0-alpha.6 adds the Plugin Center ACTIVATE/WakeActivity recovery path for the stopped/notLaunched state left by some OEMs after first install. Host and Plugin APKs must use the same signer; mixing a debug Host with the production Plugin is deterministically rejected as PYTHON_RUNTIME_PROVIDER_UNTRUSTED. Stable APK identity is bound to that exact Plugin source and Host lock.

```text
release target: 0.5.0
release state: 0.5.0 stable source candidate; protocol 1.0-1.6 and cumulative M1-M5 capabilities remain frozen with the embedded runtime stdlib-only; the exact SM003-signed 0.5.0-beta.1 arm64 APK from commit 4bbae75dbfb496995e5278684024f63ae9f71a43 was pulled from QV710AF65F with SHA-256 80FA480ACAE1C66C07DC59C9B588603B7F787E21DE72BB5A5521A2732B0C695F, byte-identical to the formal candidate, and passed all ten manual Android smoke items (10/10 PASS); the preceding exact alpha run and a matching Android-Debug run on OnePlus OPD2413 also passed 10/10, including OEM ACTIVATE recovery; deterministic item 2/3/4 materials live in examples/python/m6_manual_smoke; a stable signed artifact, exact stable smoke, stable tag, push, publication, and post-publication evidence remain outside this source claim
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
- Bounded request timeout is capped at 30 min. Explicit long-running projects have no elapsed deadline but require the Host foreground lifetime, a 2 min start lease, and a 45 s heartbeat lease; there is still one active session per process and no provider-side queue.
- A project workspace is capped at 64 MiB compressed, 8192 file entries, and 128 MiB extracted; Provider selection must satisfy the actual snapshot in all three dimensions before dispatch.
- SOURCE descriptors adopt complete Binder receiver-side PFD ownership, preserve reliable-pipe error channels, and close at terminal or session close.
- Output is delivered chunk by chunk under credits during execution; exhausted credits pause the script, accepted output precedes the single terminal, and output after terminal is forbidden.
- Structured JSON is capped at 64 KiB; at most 16 artifacts are accepted with 1024 UTF-8 bytes paths, 4 MiB per file, 8 MiB aggregate, and Host verification of exact length, EOF, and SHA-256.
- Protocol 1.5 admits at most 1024 Host calls per execution, caps each request/response at 64 KiB and text at 32 KiB, and waits at most 5 s for an ordinary Host main-thread action. Host files use 4 KiB relative paths, 32 KiB UTF-8 text, and listings of at most 128 names of 255 UTF-8 bytes each. Foreground dialogs cap titles at 256 UTF-8 bytes, content at 4 KiB, prompt defaults/replies at 32 KiB, and selection lists at 64 items of 1 KiB each and 32 KiB total; one user response may wait up to 5 min. One execution may successfully launch at most 16 scoped asynchronous non-Python Host child scripts; nested Python returns `NESTED_PYTHON_NOT_ALLOWED`, and `stop_self` cancels through process restart.
- Automator coordinates are strict integers from 0 through 1000000, while press and swipe durations range from 1 ms through 4 s; unavailable Host accessibility raises `CapabilityUnavailableError` without opening settings.
- Selector snapshots accept at most 128 nodes, depth 32, and 48 KiB of JSON; find scans at most 1024 nodes, node text is capped at 256 Unicode code points, query text at 1024 UTF-8 bytes, set text at 4 KiB, and each execution retains at most 128 node references. Incomplete scans return `SELECTOR_SCAN_LIMIT_EXCEEDED` and stale references return `STALE_NODE`.
- Screen capture retains at most 1 image per execution, caps encoded data at 4 MiB, transfers raw chunks of 32 KiB, and limits each dimension to 8192 pixels and total area to 16777216 pixels. Python verifies length, order, EOF, SHA-256, and the format signature before returning; unavailable accessibility/API raises `CapabilityUnavailableError`, while stable failures include `SCREEN_CAPTURE_FAILED`, `RESULT_LIMIT_EXCEEDED`, and `STALE_IMAGE`. Color search scans one fresh screenshot in row-major order with an optional bounded region and per-channel threshold up to 255, returning only a coordinate or miss without transferring image bytes. Template search retains at most 1 PNG/JPEG template, caps it at 1 MiB, transfers 24 KiB raw chunks, and limits dimensions to 2048, area to 1048576, search region to 4194304, and comparisons to 16777216; exact-alpha pixels participate, other pixels are wildcards, matching is deterministic row-major, and buffers are released and zeroed at terminal.
- `ocr.recognize` reuses the PNG/JPEG template envelope of 1 MiB, 24 KiB raw chunks, 2048 pixels per side, and 1048576 decoded pixels. The configured Host OCR engine returns at most 256 lines, 4 KiB strict UTF-8 per line, and 48 KiB total under the existing 60 s admission/call budget; unavailable and failed engines report `OCR_UNAVAILABLE` and `OCR_FAILED`, and uploads are always released and zeroed.
- Cancellation uses process restart rather than CPython-level cooperation; native extensions and blocking calls still require later Android validation.
- The plugin grants `INTERNET` for script-initiated standard-library networking; online pip, automatic code downloads, and runtime third-party package installation remain unsupported.

******

### Undeclared capabilities

******

- General live stdin and direct `sys.stdin` callback streaming are unavailable. Foreground interaction applies only to built-in `input()` and standard-library `getpass.getpass()` after the finite snapshot of at most 1 MiB reaches EOF. Workspace write-back, online pip, and runtime wheel downloads remain unsupported.
- There is no UI scripting, debugger, REPL, or arbitrary access to host Java objects.
- The live broker covers the complete first low-risk slice, bounded Host files, foreground dialogs, bounded engines, explicit coordinate/global automator actions, bounded selector/UI-tree snapshots/actions, bounded screen capture, `find_color`, `find_image`, and line-oriented OCR. OCR boxes/confidence/options, mutable image processing, and multi-scale matching remain undeclared.
- 32-bit Android support is not declared, and arbitrary third-party native wheels are not guaranteed.
- The current tree has API 31 arm64-v8a device smoke evidence and API 37 x86_64 16 KB-page emulator smoke evidence; neither is presented as a complete device matrix or release qualification.

******

### Roadmap

******

M4 Path A is complete; M4 Paths B and C both concluded `NOT_ADMITTED`, so the embedded runtime remains `stdlib-only`. Path C built Pillow and NumPy offline, but their complete native closures failed the dual-ABI 16 KiB ELF gate, and OpenCV had no `cp313` Android wheel; Path D remains demand-driven. M3 automation includes bounded actions, selector/UI-tree operations, screen capture, color search, PNG/JPEG template matching, and Host OCR. Historical evidence tools are not automatic release gates.

- [View ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### Release history

******

# v0.5.1

###### 2026/09/12

* `Fix` Release build failure after clean when the generated Chaquopy ProGuard rules file is missing
* `Improvement` Build verification of 16 KB page alignment for 64-bit native libraries, including manifest contract checks and JSON reports

# v0.5.0

###### 2026/08/25

* `Hint` 0.5.0 cumulative stable source candidate; the exact SM003-signed beta candidate passed all 10 Android smoke items, without claiming a stable APK, tag, or completed publication
* `Feature` M6 consolidates M1-M5 capabilities and reusable item 2/3/4 materials while fixing the lightweight alpha → beta → stable candidate and publication boundaries
* `Improvement` The 0.5.0-beta.1 arm64 APK pulled from QV710AF65F was byte-identical to the formal candidate, and the second complete ten-item run finished 10/10 PASS

# v0.5.0-beta.1

###### 2026/08/25

* `Hint` 0.5.0-beta.1 feature-freeze source candidate; the exact SM003-signed alpha candidate passed all 10 Android smoke items, without claiming a beta APK, stable release, or completed publication
* `Feature` M6 adds reusable item 2/3/4 projects and an independent artifact verifier so imports, stdin/interactive input, and structured results can be accepted repeatably
* `Improvement` The 0.5.0-alpha.6 arm64 APK pulled from QV710AF65F was byte-identical to the formal candidate, and the complete ten-item checklist finished 10/10 PASS

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


[16 KB page alignment and build verification](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/docs/16kb.md)
