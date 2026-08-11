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

> This is currently an R2 proof of concept. Runtime source and local bootstrap semantic checks are present, but Gradle configuration, Android compilation, APK inspection, Binder validation, and device acceptance have not run.

******

### Features

******

- Execute one UTF-8 Python source snapshot as `__main__`.
- Collect stdout and stderr in their original order, then deliver bounded chunks under credits.
- Report `SystemExit`, syntax errors, and runtime exceptions with a bounded structured traceback.
- Allow one active session in the runtime process with no provider-side queue.
- Retire the dedicated process after cancellation, timeout, callback death, or an isolating close path, without automatically replaying the script.

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

The build requests Python 3.13. Version 3.13.9 is the expected packaged version recorded from the current Chaquopy release information, not a verified fact until APK inspection and device execution are complete.

******

### Plugin interface

******

The host discovers and calls the plugin with the following identities:

```text
service action: org.autojs.plugin.python.RUNTIME
protocol provider id: org.autojs.python.runtime.cpython
engine: python
protocol: V1
```

The plugin accepts only a SOURCE descriptor. Workspace-archive and stdin-snapshot limits are zero, and no Context, Binder, host runtime object, or callback sink is injected into script globals.

******

### Host integration status

******

> The protocol and host wiring roadmap is progressing, but the release AARs required by this repository have not been published and verified. Installing this scaffold alone does not establish a usable end-to-end Python engine.

******

### Security and privacy

******

The source manifest requests no Android permission. The exported service requires the host signature permission and rechecks the calling UID, installed host package, and current signer set at Binder entry points. Python can still reach a Java bridge through Chaquopy, so this plugin relies on a separate Android UID, a dedicated process, and a narrow Binder capability boundary; it does not claim CPython is a security sandbox.

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

- Workspace archives, stdin snapshots, online pip, and runtime wheel downloads are unsupported.
- There is no UI scripting, debugger, REPL, or arbitrary access to host Java objects.
- There is no AutoJs6 capability broker yet; host APIs such as console, files, device, accessibility, and shell are not connected.
- 32-bit Android support is not declared, and arbitrary third-party native wheels are not guaranteed.
- Local CPython unit tests are not treated as Chaquopy, Android, Binder, or device-acceptance evidence.

******

### Roadmap

******

The independent R2 repository, static boundary, provider/bootstrap sources, and local semantic tests are present. All Gradle and ADB work is deferred while QV710AF65F runs a protected soak. Release AARs, dependency resolution, Android compilation, APK and 16 KB page checks, Binder/PFD validation, and the device matrix remain incomplete; refer to the project roadmap for checkbox status.

- [View ROADMAP.md](https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/blob/master/ROADMAP.md)

******

### Release history

******

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
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-r2-static.ps1
```

Portable bootstrap semantic tests under the machine's local CPython:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B -m unittest tools.tests.test_bootstrap -v
```

Neither check proves the Android runtime works. Gradle, APK, Binder, and device verification must be completed separately after the protected soak.

******

### Build

******

No build is run at this stage. Release configuration fails closed while protocol AARs are missing or their SHA-256 values are not locked.

The following release AARs must be staged and locked in the repository `libs` directory before a build:

```text
protocol-wire-api.aar
python-runtime-api.aar
```

The runtime is planned to use Chaquopy 17.0.0 from Maven and package only the stdlib. Dependency verification metadata, the native-library inventory, license obligations, and 16 KB page compatibility remain build-acceptance items.

******

### License

******

Project source is licensed under MPL-2.0. Chaquopy, CPython, and other third-party components remain under their respective licenses.

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
