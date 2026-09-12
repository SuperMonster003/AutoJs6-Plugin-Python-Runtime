# Samsung ARM64 / 16 KiB smoke results

On 2026-09-10, Samsung SM-A566B supplied the previously missing physical
ARM64 / 16 KiB test cell. The installed Python Runtime `0.5.0`/93 passed the
focused native-runtime probe and 20 distinct current public-engine test
methods (one clipboard method passed on retry after dismissing a system
dialog). The paired Host has three 4 KiB-aligned native libraries and Android
runs it in page-size compatibility mode. This is a Plugin compatibility
supplement, not a full Host 16 KiB qualification or the M6 stable ten-item run.

## Device and installed artifacts

| Field | Observed value |
| --- | --- |
| Connection | Samsung RDB, explicitly addressed as `localhost:31277` |
| Model | Samsung SM-A566B (`a56x`) |
| Android | 16 / API 36 |
| ABI | `arm64-v8a`; Python reports `aarch64` |
| Kernel page size | `adb shell getconf PAGE_SIZE` = `16384` |
| Kernel | `6.6.77-android15-8-abA566BXXU6BYIF` |
| Build fingerprint | `samsung/a56xnaeea_16kb/a56x:16/BP2A.250605.031.A3/A566BXXU6BYIF_OXM6BYIF:user/release-keys` |
| User | Only user 0, active |
| Clock | Workstation Asia/Shanghai; device Asia/Seoul |

The artifacts were already built locally. No APK was rebuilt or re-signed for
this run. Each installed `base.apk` SHA-256 was read on the device and matched
the local copy used for installation:

| Artifact | Version / build | APK SHA-256 |
| --- | --- | --- |
| Python Runtime, release, arm64-v8a | `0.5.0` / `93` | `757E2DC65DD023B4BD87467D26624F2459BAE2A0D971A4756D7B75C92E6AED38` |
| AutoJs6, debug, arm64-v8a | `6.8.0` / `5279` | `EF5C38F62B8CB98F2E5ED81DADEB413EBF0AC373089AB70A6006199090F198D8` |
| Host Android test APK | `org.autojs.autojs6.test` | `71F96FADE33B527AFF0B0DFEED157C7395CB5B5A231B2E4D651D3BD9785D09C9` |

All three APK signatures verified with the production SM003 certificate
SHA-256 `31A681FCFFFB3E428420CAE280DED89292B12A3B0F59E19B7A73E32A8AE4C213`.
The Plugin is not debuggable; the Host and test APK are debuggable. A matching
signer does not make that Host a production release build.

Workspace HEADs at collection were Plugin
`086f9362ca5a3338fc89b0a180b86a547aedf4c7` and Host
`94f65d301048c731f18219a846b576dcca72f035`. These are collection context;
the prebuilt APK identities above are authoritative for the tested bytes.

## Native layout and actual Python process

Both APKs pass `zipalign -c -P 16 4`. A separate ELF scan checks every
`PT_LOAD` alignment and its file-offset/virtual-address congruence modulo
16384. ZIP alignment alone would miss the Host problem.

- Plugin: all 124 packaged ELF entries pass, including the nested Chaquopy
  archives (66 AArch64 and 58 x86_64 entries; minimum LOAD alignment `0x4000`).
  Only ARM64 code was executed on this device. `dumpsys package` reports
  `pageSizeCompat=0` for the Plugin.
- Host: all three `lib/arm64-v8a/*.so` files have minimum LOAD alignment
  `0x1000`: `libc++_shared.so`, `libjackpal-androidterm5.so`, and
  `libjackpal-termexec2.so`. `dumpsys package` reports `pageSizeCompat=4`.
  Android displayed a first-launch dialog identifying AutoJs6's ELF alignment
  failure and stating that page-size compatibility mode would be used.

Android documents this warning and compatibility behavior for apps with
4 KiB-aligned native libraries in its
[16 KB backcompat guidance](https://developer.android.com/guide/practices/page-sizes#16-kb-backcompat-mode).
This run did not override the device-wide backcompat properties or the
per-app compatibility setting.

The reusable
[`arm64_16k_probe.py`](../../examples/python/arm64_16k_probe.py) ran through
`RunIntentActivity` with explicit `source_kind=python_file_v1`, the public
Host engine, and the installed Plugin. Its final published JSON reported:

| Probe | Result |
| --- | --- |
| CPython / machine | `3.13.9` / `aarch64` |
| `os.sysconf("SC_PAGE_SIZE")` / libc `getpagesize()` | `16384` / `16384` |
| `mmap.PAGESIZE` / `mmap.ALLOCATIONGRANULARITY` | `16384` / `16384` |
| `/proc/self/smaps` kernel page sizes | `[16]` KiB |
| zlib, bz2, lzma | Byte-exact compression/decompression PASS |
| Anonymous mmap / file mmap at a 16 KiB offset | PASS |
| ctypes/libffi callback | PASS |
| SQLite BLOB round trip | PASS; SQLite `3.50.4` |
| SSL context with certificate verification | PASS; OpenSSL `3.0.18` |
| Local socket pair | PASS |

The final probe finished in 1.357 seconds, with Plugin PID 13541 and Host PID
12664. Both the explicit `[result]` and the published
`device/arm64-16k.json` artifact were observed. The artifact was read back and
parsed independently. The probe inspects all process mapping page sizes:
Android can map libraries directly from `base.apk`, so a mapping need not
contain the string `libpython3.13.so`. An initial probe-development assertion
which required that filename failed; the checked-in probe removes that path
assumption and passed on this device.

## Public execution coverage

Tests used Host `PythonU1R2AcceptanceInstrumentationTest` with
`autojs.python.u1r2.public.enabled=true`. They exercise public launch/engine
paths, actual CPython Binder/PFD sessions, and the Host console/result surface.

| Coverage | Distinct methods | Final result |
| --- | ---: | --- |
| Module entry, relative imports, explicit JSON, exact binary artifact, stdout not inferred as a result | 1 | PASS |
| Project-file Unicode stdin snapshot and EOF | 1 | PASS |
| Toast, clipboard, missing-app results, invalid URL argument | 1 | PASS after dismissing system dialog |
| Device info, console levels, notification permission result | 1 | PASS |
| Scoped Host files | 1 | PASS |
| Host engine metadata, JavaScript child, nested-Python rejection | 1 | PASS |
| `engines.stop_self()` and no following statement | 1 | PASS |
| Stop active Python, changed Plugin PID, immediate successful rerun | 1 | PASS |
| More than 4 MiB of stdout and final marker | 1 | PASS |
| 90-second execution, live ticks before terminal, final marker | 1 | PASS |
| Unattended `input()` returns EOFError | 1 | PASS |
| Editor `input()` / Explorer `getpass()`, visible/hidden echo | 1 | PASS |
| Foreground alert/confirm/prompt/select | 1 | PASS |
| Background dialog rejection | 1 | PASS |
| Automator, selector, capture, find-color, find-image with accessibility unavailable | 5 | PASS, unavailable-service branch |
| OCR without an installed engine | 1 | PASS, unavailable-engine branch |
| **Total** | **20** | **All have a passing final observation** |

The first 17-method batch took 14.404 seconds and had 16 passes plus one
clipboard failure. While the system compatibility dialog owned focus,
`ClipboardService` logged a denied read for `org.autojs.autojs6` and Python
received an empty string. Dismissing that dialog, without changing code,
APKs, or clipboard policy, let the same method pass. That retry ran with the
two foreground interaction methods: `OK (3 tests)`, 6.133 seconds. The separate
90-second streaming test reported `OK (1 test)`, 91.682 seconds. No skipped
method is counted as a pass.

### Legacy R1 assertion still fails

`PythonU1R1AcceptanceInstrumentationTest` was also run and reported one
failure, in 0.654 seconds. Its first Python script successfully checked
CPython 3.13.9, Unicode stdin, EOF, standard-library operations and relative
imports, and completed in 0.583 seconds. The failure was in the Host test's
console assertion: it expects `U1R1 input> ` and the following result marker
to be adjacent, but its helper inserts `\n` between independently streamed
console entries.

This legacy test is **FAIL**, excluded from the 20 passes above. It failed
before the second workspace was executed, so this run does not claim that
test's sequential-workspace isolation coverage. A Host test change should
compare the ordered output without inventing separators between chunks,
retain the exact byte-count/terminal assertions, and then rerun both
workspaces. No Host source was changed during this supplemental run.

## Reproduction and retained observations

Install a matching-signer Host, Plugin and Host test APK, record their exact
hashes, and inspect any first-launch system dialog before interactive tests.
For example, the streaming observation can be repeated with:

```powershell
adb -s localhost:31277 shell am instrument -w -r `
  -e autojs.python.u1r2.public.enabled true `
  -e class org.autojs.autojs.engine.PythonU1R2AcceptanceInstrumentationTest#configuredNinetySecondProjectStreamsBeforeTerminalAndCompletes `
  org.autojs.autojs6.test/androidx.test.runner.AndroidJUnitRunner
```

Run `examples/python/arm64_16k_probe.py` as an ordinary Python file from the
Host editor or Explorer on an ARM64 / 16 KiB device. It intentionally asserts
the target platform and CPython version; a desktop or a 4 KiB device does not
qualify. Success prints `ARM64-16K-PROBE-PASS`, returns explicit JSON, and
publishes `device/arm64-16k.json`. It uses local native operations and makes no
external network request. The ADB-only run here staged the file in a unique
Host-private directory and used the supported persisted-file Intent extras.

Raw local observations are retained under the ignored directory
`build/reports/device/samsung-arm64-16k-20260910-102847/`, including the APK
copies, installed hashes, `plugin-elf-alignment.json`,
`host-elf-alignment.json`, `u1r1-public.txt`, `r2-core.txt`,
`r2-core-selection.txt`, `r2-foreground.txt`, `r2-streaming-90s.txt`,
`ui-after-core.xml`, `clipboard-logcat.txt`, `public-console.txt`, and
`arm64-16k-result.json`. This committed document preserves the concise result
when those local build outputs are unavailable.

## Remaining coverage and device state

The full M6 stable checklist remains open. This run does not cover five-minute
foreground-service survival, FIFO/queued cancellation, scheduled launches,
Plugin disable/re-enable, a production Host build, eligible accessibility/OCR
success paths, external HTTPS, or project-local third-party packages. The
native-package decisions for Pillow/NumPy/OpenCV are unchanged.

The follow-up Host work is to replace/rebuild the three listed native
libraries, verify ELF and ZIP alignment on the final APK, and repeat the
public paths without page-size compatibility mode. Removing a warning alone
does not address the ELF layout.

Instrumentation cleaned its test projects and transport snapshots. The probe
directory, published probe artifact and this run's `/data/local/tmp` files
were removed after collection. Accessibility stayed disabled (service list
`null`), screen timeout stayed 300000 ms, and stay-awake stayed 0. The newly
installed Host, Plugin and test APK were retained for further device testing.
