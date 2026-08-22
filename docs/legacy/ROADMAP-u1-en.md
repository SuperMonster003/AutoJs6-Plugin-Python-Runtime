# Python Runtime Plugin Roadmap

Status: the immutable Plugin `0.1.0` release track is closed. Current work is
the post-`0.1.0` Python Usability Track U1, organized as U1-R0 through U1-R6.
U1 prioritizes ordinary Python semantics, `input()` and predictable `import`
behavior before broader AutoJs6 capabilities.

This roadmap is an executable gate specification. A checked source/static or
portable-Python item never substitutes for Android compilation, Binder/PFD,
APK/native, device-matrix or production-release evidence.

## Evidence levels

| Level | Exact claim | Explicit non-claim |
| --- | --- | --- |
| E0 `SOURCE_STATIC_ONLY` | Contract, manifest and static verifier agree | No CPython, Android or device execution |
| E1 `PORTABLE_CPYTHON_ONLY` | Portable bootstrap cases passed on the recorded local Python | No Chaquopy, Binder or Android proof |
| E2 `ANDROID_BUILD_ONLY` | Affected JVM tests, Android compile and APK packaging passed | No real Binder/CPython device execution |
| E3 `BINDER_CPYTHON_DEVICE_PARTIAL` | Exact Host/Plugin artifacts executed on the recorded device cell | No unrecorded API/ABI coverage |
| E4 `DEVICE_MATRIX_ROBUSTNESS` | Declared compatibility and recovery cells passed | No public-release fact |
| E5 `PRODUCTION_RELEASE` | Independent public artifact verification and production receipt passed | No capability beyond the receipt |

Development reports must record the Git HEAD, tracked-diff state and untracked
paths. A dirty-tree report is `CURRENT_TREE_*` evidence and cannot authorize a
release. Generated U1 reports live under `build/reports/python/u1/`; they never
overwrite a `0.1.0` report.

## Immutable `0.1.0` historical release

- [x] Keep Python in an independently installed APK and dedicated
  `:python_runtime` process. CPython, Chaquopy and Python native libraries never
  load into the Host process.
- [x] Keep `.py` fail-closed: an unavailable, disabled, incompatible or dead
  provider never falls back to Rhino, RootAutomator or another legacy engine.
- [x] Freeze Chaquopy `17.0.0`, CPython `3.13.9`, 64-bit
  `arm64-v8a`/`x86_64`, stdlib-only and trusted-local/non-sandbox semantics.
- [x] Freeze Plugin producer/tag commit
  `4cc4187137e3c1060aa0444b482377afafb6a032` as `v0.1.0`, paired with Host
  producer `2caddcb763b39f0bf450909742fa6ec4caba27a8` / `6.8.0` / `5275`.
- [x] Preserve
  `build/reports/python/r6-0.1.0-production-receipt.json` as the independent
  E5 publication record. U1 work must not edit or relabel it.
- [x] Preserve the historical API 31 arm64-v8a concentrated device evidence.
  `x86_64` remains packaging-only in that receipt.

### R6-P2: final source and Host-pair freeze (historical)

The `0.1.0` source and exact Host API distribution were frozen before its
artifact-producing commit. Existing RC receipts are historical and remain
immutable; they cannot be promoted to U1 evidence. A complete API 24-36 by ABI matrix is not automatic
for U1: expand device work only for a concrete
compatibility, ABI, lifecycle or security risk. The production receipt, rather
than mutable checklist prose, remains the authority for the old release.

## U1 invariants and evidence policy

- [x] Retain exact-component selection, UID/package/signer validation, one
  active provider session, one terminal event, idempotent cancel/close, bounded
  metadata/PFD transport and no replay after dispatch.
- [x] Treat user-selected local Python as trusted for the Plugin UID, not as
  hostile-code sandboxing. Chaquopy's Java bridge does not grant Host-process
  objects or permissions.
- [x] Do not publish a capability flag until Host negotiation, Provider
  admission, bootstrap behavior, cleanup and negative cases are implemented.
  The R1 stdin flag was enabled only after those source and E2 gates existed.
- [x] Keep online pip, runtime wheel download and arbitrary Host Java-object
  injection disabled throughout U1.
- [x] Run Gradle invocations serially. Device commands require an explicitly
  authorized serial and must verify package/process cleanup afterward; no
  device command was run for R0/R1 E2.
- [x] Reuse the existing protocol stdin field without changing shared API/AAR
  sources. If a later phase changes shared protocol/API source, regenerate and
  lock the exact release AAR distribution before Plugin release evidence is
  collected.

## U1-R0: capability truth and Python semantics contract

Priority: complete. Scope: documentation, portable fixtures and a fail-closed
gate only. R0 itself did not change runtime code or advertised capabilities;
the later R1 implementation updated those capabilities.

### Checklist

- [x] Maintain `docs/python/PYTHON_SEMANTICS_CONTRACT.md` as the normative
  current-versus-target contract for source encoding, execution globals,
  stdin, imports, process-state restoration and unsupported behavior.
- [x] Maintain the machine-readable fixture
  `tools/tests/fixtures/u1-r0-python-semantics-cases.json` with unique case IDs,
  current claims, target phases and exact expected portable outcomes.
- [x] Cover ordinary syntax and builtins: literals, Unicode, operators,
  branching, loops, functions, closures, comprehensions, generators, classes,
  pattern matching, exceptions, context managers and `asyncio.run()`.
- [x] Cover execution state: `__name__`, `__file__`, `sys.argv`, cwd,
  `sys.path`, stdout/stderr order, `SystemExit`, syntax/runtime exceptions and
  state restoration.
- [x] Classify imports as builtin/frozen, stdlib, workspace module, regular or
  namespace package, third-party package, or Android-unavailable module.
- [x] Record the implemented U1-R1 stdin capability as a finite, pre-supplied
  snapshot with a 1 MiB maximum. Do not call it interactive input.
- [x] Generate `build/reports/python/u1/r0-python-usability-gate.json` with the
  actual local Python version, case counts, source identity and explicit false
  Android/device/publication claims.
- [x] Keep the U1-R0 verifier read-only with respect to tracked source; its only
  output is the ignored generated report.

### Commands

```powershell
Set-Location D:\idea-projects\AutoJs6-Plugin-Python-Runtime
$env:PYTHONDONTWRITEBYTECODE = '1'
python -B -m unittest tools.tests.test_u1_r0_python_usability_source -v
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-u1-r0-python-usability.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-r2-static.ps1
git diff --check
```

### Evidence and exit condition

- E0/E1: `build/reports/python/u1/r0-python-usability-gate.json`.
- Exit: the contract, fixture, test and verifier agree; all executable fixture
  cases pass; unsupported/planned cases are not executed or promoted; the
  report says `androidCompiled=false`, `deviceVerified=false` and
  `published=false`.

### Blockers

- No device is required. If local Python is not `3.13.9`, the report must keep
  its actual version and remain portable evidence only.
- A dirty tree does not block development verification, but its report cannot
  become release evidence.

## U1-R1: core Python semantics, `input()` and predictable imports

Priority: highest. R1 first closes bounded static stdin and import semantics;
true interactive prompt/reply belongs to R2.

### R1-A: admission and lifecycle hardening

- [x] Accept only strict UTF-8 Python source, with an optional UTF-8 BOM;
  reject invalid UTF-8, NUL and a conflicting non-UTF-8 encoding cookie before
  CPython dispatch.
- [x] Start a 5-second Provider-side start lease when a session is opened. A
  client which never calls `start()` has its session closed and its slot/PFDs
  released without executing user code. Lease expiry does not retire the
  runtime generation.
- [x] Enforce the declared minimum Host versionCode at the Provider Binder
  boundary in addition to normal Host discovery checks.
- [x] Restore `sys.stdin`, stdout, stderr, argv, path, cwd, importer cache and
  project modules on success, exception, output limit, cancel and timeout.
- [x] Prove in portable/JVM tests that two sequential workspaces with the same
  module name cannot reuse
  the previous workspace module.

### R1-B: bounded stdin snapshot and `input()`

- [x] Activate the already-declared optional `STDIN` PFD only after validating
  kind, unique descriptor index, declared length, exact EOF, SHA-256,
  reliable-pipe error and Provider maximum.
- [x] Start with a Provider maximum of 1 MiB; raise it only with a
  concrete use case and evidence.
- [x] Install an execution-local UTF-8 text stdin over the verified bytes.
  `input(prompt)` writes the prompt to stdout and consumes LF/CRLF, Unicode,
  multiple lines and a final line without newline with ordinary CPython
  semantics.
- [x] Support `sys.stdin.read()`, `readline()`, `readlines()` and
  `sys.stdin.buffer.read()` with bounded snapshot behavior.
- [x] An omitted or empty snapshot produces immediate EOF/`EOFError`; it never
  reads the Plugin process stdin or blocks indefinitely.
- [x] Advertise `supportsStdinSnapshot=true` and nonzero `maxStdinBytes` only
  after the Provider, Host client, negotiation, tests and cleanup paths exist.
- [x] Add an immutable Host execution option which snapshots stdin bytes into
  a private PFD. Existing ordinary launches default to empty stdin and never
  display surprise UI.
- [x] Keep the current public-launch limitation explicit: no public Host launch
  surface provides the snapshot yet, so label the
  result `TRANSPORT_AVAILABLE_UI_NOT_AVAILABLE`, not complete user-facing
  `input()` support.

### R1-C: `import xxx` and basic-language matrix

- [x] Execute the R0 syntax/builtin matrix through the updated bootstrap and
  retain exact expected output or exception checks.
- [x] Verify representative stdlib import semantics with the portable
  bootstrap matrix.
- [x] Verify the packaged CPython stdlib on an authorized device/API cell,
  including `json`, `pathlib`, `re`, `math`, `datetime`, `collections`,
  `decimal`, `fractions`, `asyncio` and `importlib`; report
  platform/native-dependent modules separately.
- [x] Verify in portable/JVM tests project entry-sibling, project-root,
  regular-package, namespace-package, re-export, circular and dynamic
  `importlib` imports.
- [x] Preserve explicit Python-project context when its admitted entry is run
  from Project Launcher, Explorer or Editor.
- [x] Do not implicitly snapshot an arbitrary standalone script's parent
  directory.
- [x] Add a safe missing-adjacent-module hint which directs the user to an
  explicit Python project without leaking private paths.
- [x] Keep third-party imports standard and deterministic: an absent package
  raises `ModuleNotFoundError`; no online pip or hidden fallback occurs.
- [x] Keep file-mode `__package__` semantics truthful and derive normalized
  package context for a nested entry in an explicitly admitted project, so
  ordinary relative imports work without widening the workspace. Explicit
  module-entry mode remains R2 work.

### Commands

```powershell
Set-Location D:\idea-projects\AutoJs6-Plugin-Python-Runtime
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-u1-r1-core-semantics.ps1
git diff --check
```

The verifier runs the portable unittest discovery and Plugin
`:app:testDebugUnitTest :app:assembleDebug`. If Host integration source changes,
pass the Host repository so the same gate also runs its three required tasks:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\verify-u1-r1-core-semantics.ps1 `
  -HostRepository D:\idea-projects\AutoJs6
```

The E3 transaction is a separate, opt-in, non-soak gate. It requires both
repositories to be clean and pinned to exact commits, an already-passing E1/E2
functional report, exact APK hashes, one explicit serial, a frozen user list
and two current-run authorization switches. The runner installs only when all
three packages are absent for every frozen user and globally; it snapshots and
rechecks every installed APK, then uninstalls only runner-owned bytes in reverse
order. The offline verifier alone may write the canonical report.

```powershell
if ($PSVersionTable.PSVersion.Major -lt 7) { throw 'U1-R1 E3 requires PowerShell 7+' }
$plugin = 'D:\idea-projects\AutoJs6-Plugin-Python-Runtime'
$hostRepo = 'D:\idea-projects\AutoJs6'
$adb = 'E:\.android\sdk\platform-tools\adb.exe'
$aapt2 = 'E:\.android\sdk\build-tools\37.0.0\aapt2.exe'
$apksigner = 'E:\.android\sdk\build-tools\37.0.0\apksigner.bat'
$signer = '31a681fcfffb3e428420cae280ded89292b12a3b0f59e19b7a73e32a8ae4c213'

Set-Location $plugin
& .\tools\verify-u1-r1-core-semantics.ps1 `
  -HostRepository $hostRepo

Set-Location $hostRepo
.\gradlew.bat --console=plain `
  :app:assembleAppDebug :app:assembleAppDebugAndroidTest

Set-Location $plugin
$hostCommit = (git -C $hostRepo rev-parse HEAD).Trim()
$pluginCommit = (git rev-parse HEAD).Trim()
$gate = (Resolve-Path .\build\reports\python\u1\r1-core-semantics-gate.json).Path
$fixture = (Resolve-Path .\tools\tests\fixtures\u1-r1-device-observation-contract.json).Path
$hostApk = (Resolve-Path "$hostRepo\app\build\outputs\apk\app\debug\autojs6-v6.8.0-arm64-v8a.apk").Path
$testApk = (Resolve-Path "$hostRepo\app\build\outputs\apk\androidTest\app\debug\app-app-debug-androidTest.apk").Path
$pluginApk = (Resolve-Path .\app\build\outputs\apk\debug\autojs6-plugin-python-runtime-v0.2.0-alpha.1-arm64-v8a.apk).Path
$gateSha = (Get-FileHash -Algorithm SHA256 $gate).Hash.ToLowerInvariant()
$fixtureSha = (Get-FileHash -Algorithm SHA256 $fixture).Hash.ToLowerInvariant()
$hostSha = (Get-FileHash -Algorithm SHA256 $hostApk).Hash.ToLowerInvariant()
$testSha = (Get-FileHash -Algorithm SHA256 $testApk).Hash.ToLowerInvariant()
$pluginSha = (Get-FileHash -Algorithm SHA256 $pluginApk).Hash.ToLowerInvariant()
$stamp = [DateTimeOffset]::UtcNow.ToString('yyyyMMddTHHmmssZ')
$raw = Join-Path $plugin "build\reports\python\u1\r1-binder-cpython-device-run-$stamp-QV710AF65F-$($hostCommit.Substring(0,12))-$($pluginCommit.Substring(0,12)).json"

& .\tools\device\run-u1-r1-binder-cpython-device.ps1 `
  -Serial QV710AF65F -ExpectedApi 31 -ExpectedAbi arm64-v8a `
  -ExpectedUserIds @(0, 10) `
  -HostRepository $hostRepo -PluginRepository $plugin `
  -ExpectedHostCommit $hostCommit -ExpectedPluginCommit $pluginCommit `
  -FunctionalGate $gate -FunctionalGateSha256 $gateSha `
  -ObservationFixture $fixture -ObservationFixtureSha256 $fixtureSha `
  -HostApk $hostApk -HostSha256 $hostSha `
  -HostTestApk $testApk -HostTestSha256 $testSha `
  -PluginApk $pluginApk -PluginSha256 $pluginSha `
  -ExpectedSignerSha256 $signer `
  -AdbPath $adb -Aapt2Path $aapt2 -ApkSignerPath $apksigner `
  -Output $raw -ConfirmNoActiveSoak -ConfirmDeviceMutation

$rawSha = (Get-FileHash -Algorithm SHA256 $raw).Hash.ToLowerInvariant()
& .\tools\verify-u1-r1-binder-cpython-device.ps1 `
  -RawReport $raw -RawReportSha256 $rawSha `
  -ExpectedSerial QV710AF65F -ExpectedApi 31 -ExpectedAbi arm64-v8a `
  -ExpectedUserIds @(0, 10) `
  -HostRepository $hostRepo -PluginRepository $plugin `
  -ExpectedHostCommit $hostCommit -ExpectedPluginCommit $pluginCommit `
  -FunctionalGate $gate -FunctionalGateSha256 $gateSha `
  -ObservationFixture $fixture -ObservationFixtureSha256 $fixtureSha `
  -HostApk $hostApk -HostSha256 $hostSha `
  -HostTestApk $testApk -HostTestSha256 $testSha `
  -PluginApk $pluginApk -PluginSha256 $pluginSha `
  -ExpectedSignerSha256 $signer `
  -AdbPath $adb -Aapt2Path $aapt2 -ApkSignerPath $apksigner
```

### Evidence and exit condition

- E1/E2 aggregate:
  `build/reports/python/u1/r1-core-semantics-gate.json`. It records each
  command, output digest, Plugin/optional Host source identity and explicit
  false Binder/device/release claims.
- E3: `build/reports/python/u1/r1-binder-cpython-device.json`, generated only
  by an authorized exact-device runner.
- Current status: E1 portable/JVM and E2 Android build gates are complete. E3
  is complete only when the canonical report above says `PASS` and binds the
  exact clean Host/Plugin commits, three APK hashes, signer, observation
  contract and restored device state. The accepted cell is intentionally only
  QV710AF65F / API 31 / arm64-v8a; it is not an x86_64 run, device matrix,
  production receipt, published artifact or release authorization.
- Functional exit: all R1 source/portable/Android-build gates pass and flags
  truthfully match implementation. Acceptance exit: exact Host/Plugin APKs
  prove stdin PFD, real CPython `input()`, project imports, sequential-session
  isolation and cleanup on an authorized device.

### Blockers

- Static stdin is not real-time interaction. The later R2 prompt/reply callback
  therefore uses an explicit protocol minor with golden-wire, AAR and Host-lock
  coverage rather than relabeling the already-declared stdin field.
- Local CPython and APK packaging cannot close the E3 acceptance box. A raw
  device run also cannot close it until the offline verifier reproduces all
  bindings and writes the canonical `PASS` report.

## U1-R2: module entry, live I/O and structured results

### Checklist

- [x] Add explicit `entryMode=file|module`; module mode uses a normalized dotted
  name and correct `__package__`, `__spec__`, `sys.path[0]` and package-relative
  imports. File mode remains ordinary script execution.
- [x] Move stdout/stderr credit and backpressure into execution time, preserving
  ordered partial output before cancel/timeout and forbidding output after the
  terminal event.
- [x] If interactive `input()` is added, use execution-scoped typed prompt IDs,
  size/deadline/echo policy and one reply; background launches fail immediately
  without opening UI.
- [x] Bind input waits to cancellation, timeout, Binder death and generation
  retirement.
- [x] Add bounded structured JSON results and optional output artifacts with
  count, path, size and SHA-256 limits. Never infer a result from stdout text.

### Commands and evidence

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-u1-r2-module-io.ps1 -HostRepository ..\AutoJs6
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-u1-r2-interactive-input.ps1 -HostRepository ..\AutoJs6
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-u1-r2-structured-results.ps1 -HostRepository ..\AutoJs6
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-u1-r2-e3-functional.ps1 -HostRepository ..\AutoJs6
.\gradlew.bat --console=plain :app:testDebugUnitTest
.\gradlew.bat --console=plain :app:assembleDebug
```

- E0/E2: `build/reports/python/u1/r2-module-io-contract.json`,
  `build/reports/python/u1/r2-interactive-input-contract.json`, and
  `build/reports/python/u1/r2-structured-results-contract.json`.
- E2.5 exact-artifact readiness:
  `build/reports/python/u1/r2-e3-functional-gate.json`.
- E3: `build/reports/python/u1/r2-binder-cpython-device.json`, produced only
  from a new R2 raw transaction by the offline verifier. The runner, verifier,
  frozen five-selector observation fixture, authority parameters and complete
  operator workflow are documented in
  `docs/python/U1_R2_DEVICE_EVIDENCE.md`.
- Current R2 status: module entry, execution-time output streaming, foreground
  interactive built-in input, explicit bounded JSON results, and optional
  output artifacts are complete through E2. All three reports have
  `phaseStatus=PARTIAL` and `r2Complete=false` because R2 E3 remains unverified.
  Module entry is protocol 1.2. Interactive input is protocol 1.3 with typed
  monotonic prompt IDs, one-shot bounded replies, foreground-only Host UI, and
  waits tied to cancel/timeout/Binder death/close/generation retirement.
  Protocol 1.4 adds a request-scoped result policy, one explicit strict JSON
  value, and optional regular-file artifacts bounded by count, normalized UTF-8
  path, per-file/aggregate size, exact descriptor references and SHA-256. The
  Plugin sends immutable private snapshots, the Host requires exact length/EOF
  and digest, and neither side infers results from stdout. All extensions have
  golden-wire compatibility, required-for-reader fields, explicit provider
  capabilities and a hash-locked local Host AAR triplet. The R2 E3
  instrumentation matrix and fail-closed exact-artifact tools are implemented:
  public module/result/artifact, Binder prompt/reply with pre-terminal output,
  artifact-limit recovery, cancel/rebind and timeout/rebind each run as an
  independent selector. Their AndroidTest source set compiles, but no R2 device
  transaction or canonical R2 E3 report has been executed. The current Host
  and Plugin trees remain dirty and also contain unrelated in-progress work,
  so the development triplet and local build results are not stable-release
  provenance.
- Exit: file/module semantics are distinct; each published I/O/result capability
  has positive, limit, cancel, timeout, death and cleanup evidence.
- Remaining boundary: no `Context`, Binder, Host callback object or arbitrary
  `Bundle` is injected into Python; the implemented UI is Host-owned and
  foreground-authorized. The functional implementation is closed through E2;
  exact-artifact Binder/CPython device evidence at E3 remains open until an
  authorized explicit-serial run from clean commits passes restoration and its
  raw evidence is reproduced by the offline verifier.

## U1-R3: offline dependency packs

### Checklist

- [ ] Define a signed, immutable package-pack manifest: package/version,
  Python/ABI tags, file digests, signer, license, SBOM and source URL.
- [ ] Keep online pip, runtime downloads and implicit index resolution disabled.
- [ ] Implement pure-Python wheels first; verify packages, submodules,
  resources and metadata without polluting another execution environment.
- [ ] Reject tampered, conflicting, unpinned, oversized or incompatible packs
  before user code starts.
- [ ] Gate native wheels separately for CPython 3.13 ABI, each Android ABI,
  16 KiB page compatibility, crash/OOM behavior and license obligations.
- [ ] Load package native code only in the Plugin process.

### Commands, evidence, exit and blockers

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-u1-r3-offline-packages.ps1
.\gradlew.bat --console=plain :app:testDebugUnitTest
.\gradlew.bat --console=plain :app:assembleDebug
```

- E0/E2: `build/reports/python/u1/r3-package-pack-contract.json`.
- E3: `build/reports/python/u1/r3-pure-python-import-device.json`.
- E4: `build/reports/python/u1/r3-native-wheel-matrix.json`, only if native
  wheels are actually promoted.
- Exit: at least one pinned pure-Python pack imports reproducibly offline and
  all negative admission cases fail closed. Native wheels are an independent
  sub-gate, not a disguised pure-Python success.
- Blocker: missing license/SBOM, wheel-tag drift or unverified native ABI/page
  compatibility prevents that pack from being advertised.

## U1-R4: explicit AutoJs6 capability broker

### Checklist

- [x] Retain the `0.1.0` immutable read-only
  `autojs6.app/device/execution/project` snapshot API.
- [ ] Define a versioned execution-scoped capability catalog. Every operation
  has a grant, pure-data request/result schema, timeout, quota and error code.
- [ ] Add lower-risk capabilities first: clipboard, app query/explicit Intent,
  bounded file selection and bounded network proxy.
- [ ] Split UI automation into read-only tree snapshots and explicit actions;
  selectors and nodes cross the boundary only as bounded data.
- [ ] Bind each call to execution ID, Provider UID and terminal state. Reject
  calls after terminal and prevent background execution from borrowing a
  foreground grant.
- [ ] Keep unavailable capabilities fail-closed; never recover Host privileges
  through Chaquopy's Plugin-local Java bridge.

### Commands, evidence, exit and blockers

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-u1-r4-capability-broker.ps1
```

- E0/E2: `build/reports/python/u1/r4-capability-catalog.json`.
- E3: one independently named device report per promoted capability.
- Exit: at least one new capability completes Host/Plugin/device flow; every
  unfinished entry remains `promoted=false` and default-off.
- Blocker: a capability that cannot be bounded, identity-bound, timed out or
  cancelled cannot enter the public catalog.

## U1-R5: long jobs, recovery and compatibility

### Checklist

- [ ] Add a separate long-job mode with foreground notification, heartbeat,
  lease, one terminal event and process-level cancellation; do not simply
  increase the ordinary 60-second timeout.
- [ ] Exercise callback stalls, blocking FDs, native blocking, storage
  exhaustion, Plugin crash/OOM and Host death.
- [ ] Prove no orphan session, descriptor, workspace, package, process or
  unrecoverable slot remains after every terminal path.
- [ ] Cover the minimum Android boundary, a current Android arm64 16 KiB cell
  and an x86_64 runtime cell for the exact candidate artifacts.
- [ ] Add pressure or soak only for an identified risk; diagnostics and shorter
  runs remain clearly labeled and cannot replace a formal failed gate.

### Commands, evidence, exit and blockers

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-u1-r5-robustness-evidence.ps1
```

- E4: `build/reports/python/u1/r5-device-matrix.json` and
  `build/reports/python/u1/r5-recovery.json`.
- Exit: every capability selected for the next stable release has
  risk-proportional compatibility and clean-recovery evidence bound to exact
  Host/Plugin/APK/signer/device identities.
- Blocker: a protected or active-soak device cannot be touched without explicit
  authorization. An alternate-device diagnostic does not replace its named
  formal cell.

## U1-R6: source freeze, release and independent receipt

### Checklist

- [ ] Freeze the actually completed U1 capability set. Incomplete features stay
  capability-false and do not silently become release requirements.
- [ ] Freeze Plugin version, minimum Host version, protocol/AAR identity,
  signer, dependency locks, notices and SBOM on clean source trees.
- [ ] If Host/shared API changed, regenerate and consume the exact release AAR
  distribution before building Plugin release APKs.
- [ ] Build arm64-v8a, x86_64 and universal APKs; inspect permission, signer,
  native inventory, 16 KiB properties, notices and dependency hashes.
- [ ] Run a concentrated exact-artifact E3/E4 suite covering U1-R1 stdin/import,
  U1-R2 I/O/results and every promoted package/capability plus
  cancel/timeout/death/rebind/cleanup.
- [ ] Generate pre-publication provenance with `published=false`.
- [ ] Push the exact source/tag, publish only approved assets, independently
  download them and verify remote commit, signer, size and SHA-256.
- [ ] Generate a new production receipt containing the release URL/time, tag
  commit, Host pair, AAR manifest, asset hashes, device/ABI coverage, owners and
  explicit limitations. Never overwrite the `0.1.0` receipt.

### Commands and evidence

R6 must add version-specific source, artifact, concentrated-device and stable
release verifiers modeled after the existing `verify-r6-*` tools. Their exact
commands and output names are frozen before the release candidate is built.

- E2: new release-source and APK/native reports.
- E3/E4: new exact-artifact concentrated acceptance reports.
- E5: a new versioned production receipt under
  `build/reports/python/u1/`, independently reproduced from public assets.
- Exit: only the independent receipt establishes `published=true` and stable
  completion.
- Blocker: any dirty source, stale AAR lock, mismatched signer/hash, missing
  cleanup proof or failed formal evidence keeps release authorization false.

## Immediate deployment order

1. [x] U1-R0 documentation, fixture, portable tests and generated E0/E1 gate
   are complete.
2. [x] U1-R1 source, portable/JVM and Android-build work is complete through
   E2, including lifecycle/encoding, bounded stdin transport/bootstrap, Host
   option and the portable import matrix.
3. [x] Capture exact-artifact E3 evidence for packaged CPython through the
   frozen short-running non-soak transaction on QV710AF65F / API 31 /
   arm64-v8a; the canonical report is the authority for this checkbox.
4. [x] Complete U1-R2 module entry, execution-time output, scoped interactive
   input, explicit structured JSON, and bounded artifact transport through E2.
5. [ ] Capture R2 exact-artifact Binder/CPython E3 evidence without treating
   the earlier R1 device receipt as coverage of the new protocol 1.2-1.4 work.
   The dedicated five-selector fixture, Host instrumentation, exact-device
   runner, offline verifier and E3 functional gate are ready; an authorized
   clean-commit device transaction and canonical report are still required.
6. Commit Plugin and any changed Host repository separately; each repository
   must end the implementation session clean while preserving unrelated work.
