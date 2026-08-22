# U1-R2 exact-artifact Binder/CPython device evidence

Status: tooling and instrumentation prepared; device transaction not executed.
This document does not claim R2 E3 completion, a device matrix, production
evidence, publication or release authorization.

## Purpose and evidence boundary

R2 protocols 1.2 through 1.4 add module entry, execution-time output,
interactive prompt/reply, explicit structured JSON and output artifacts. The
earlier R1 device receipt predates those extensions and cannot be reused or
renamed as R2 evidence.

The R2 flow therefore has its own frozen observation contract, raw transaction
scope, claims, raw filename prefix and canonical output:

- observation contract:
  `tools/tests/fixtures/u1-r2-device-observation-contract.json`;
- exact-device runner: `tools/device/run-u1-r2-binder-cpython-device.ps1`;
- offline verifier: `tools/verify-u1-r2-binder-cpython-device.ps1`;
- readiness gate: `tools/verify-u1-r2-e3-functional.ps1`;
- raw output prefix: `r2-binder-cpython-device-run-`;
- canonical output:
  `build/reports/python/u1/r2-binder-cpython-device.json`;
- raw/canonical scope: `U1_R2_BINDER_CPYTHON_EXACT_DEVICE_CELL`;
- maximum evidence level: `BINDER_CPYTHON_DEVICE_PARTIAL`.

Even after a successful cell, `deviceMatrixVerified`, `productionEvidence`,
`published` and `releaseAuthorized` remain false. R2 E3 is one exact
API/ABI/device cell, not a stable release receipt.

## Frozen selector matrix

Every selector is launched in a separate instrumentation invocation. A failure,
skip, assumption violation, extra test, wrong observed class/method, malformed
status stream or nonzero instrumentation exit fails the transaction.

| Selector ID | Instrumentation method | Evidence focus |
| --- | --- | --- |
| `public-module-result-artifact` | `PythonU1R2AcceptanceInstrumentationTest#publicModuleEngineReturnsExplicitJsonAndExactArtifactWithoutInferringStdout` | Public engine routing, explicit module/runpy metadata, package-relative import, explicit canonical JSON, JSON-looking stdout remaining diagnostic-only, one Host-owned artifact with exact length/EOF/SHA-256/bytes and defensive copies |
| `binder-interactive-stream` | `PythonRuntimeU1R2BinderInstrumentationTest#interactivePromptReplyStreamsBeforeTerminalAndKeepsStdoutOutOfResult` | Exact component bind, pinned callback UID, started → stdout → typed prompt → one bounded UTF-8 reply → result ordering, prompt ID/policy checks, stdout/result independence |
| `binder-artifact-limit-recovery` | `PythonRuntimeU1R2BinderInstrumentationTest#oversizedArtifactPublishesNoPartialResultThenNextExactBindSucceeds` | Per-artifact request limit, typed `OUTPUT_ARTIFACT_REJECTED` in the `RESULT` phase, no partial result/descriptors and a distinct successful request after an exact bind |
| `cancel-rebind` | `PythonRuntimeRealPluginCancelRebindDiagnosticTest#cancelAfterStartedKillsOldBinderThenExactRebindRunsFiniteRequestOnce` | Cancel after start, typed cancellation, old Binder death, no replay, exact rebind with a new runtime generation and one finite recovery execution |
| `timeout-rebind` | `PythonRuntimeRealPluginTimeoutRebindDiagnosticTest#providerTimeoutFailsBeforeOldBinderDeathThenExactRebindRunsFiniteRequest` | Provider execution deadline, typed timeout before old Binder death, no Host cancel/replay, exact rebind with a new runtime generation and one finite recovery execution |

The public selector intentionally does not automate the foreground dialog.
Foreground-only authorization and background-UI denial remain covered at E2.
The direct Binder selector exercises the same typed prompt/reply wire contract
without depending on UI automation or timing sleeps.

## Prepare the E3 functional gate

Run from the Plugin repository without an attached-device requirement:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-u1-r2-e3-functional.ps1 -HostRepository ..\AutoJs6
```

The gate reruns and binds all three R2 E2 partial contracts, the Plugin JVM/APK
work they cover, the frozen Python Runtime Host API/app targets, the AndroidTest
compilation, and both the Host app and Host test APK packaging. It does not run
the unrelated full Host app unit-test suite. It writes
`build/reports/python/u1/r2-e3-functional-gate.json` with role
`CURRENT_TREE_R2_E3_FUNCTIONAL_GATE` and with all device/publication claims
false.

The exact-device runner accepts the gate only when both recorded repositories
are clean and match the explicitly supplied commits. A gate produced from a
dirty development tree is useful for local verification but is deliberately
ineligible for E3 evidence.

## Authority and immutable inputs

The runner has no device auto-discovery. An operator must explicitly provide:

- exact ADB serial, expected API, primary ABI and the complete sorted Android
  user-ID inventory (including user 0);
- clean Host and Plugin repository paths and exact commit IDs;
- the E3 functional gate path and SHA-256;
- the canonical R2 observation fixture path and SHA-256;
- exact Host, Host AndroidTest and Plugin APK paths and SHA-256 values;
- the one expected APK signer certificate SHA-256;
- exact `adb`, `aapt2` and `apksigner` executable paths;
- a new ignored raw-output path whose filename starts with
  `r2-binder-cpython-device-run-`;
- current-run `-ConfirmNoActiveSoak` and `-ConfirmDeviceMutation` switches.

Do not infer a serial from `adb devices`, an environment variable, an earlier
R1 report or a remembered device. `ANDROID_SERIAL`, when set, must exactly equal
`-Serial`. Device authority must identify the intended current cell.

The transaction refuses a competing device/Gradle client, serializes itself
with a per-serial global mutex, requires all three packages to be fully absent
for every frozen user, installs without replacement only for user 0, pulls each
installed artifact back for equality verification, runs every selector, then
uninstalls in reverse order and verifies users, package absence and relevant
process cleanup. Restoration failure is reported as `FAILED_RESTORATION` and
cannot be hidden by a successful test.

## Exact-device runner template

The following is a template, not authority to run against any device. Replace
every placeholder with current, independently verified values:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\device\run-u1-r2-binder-cpython-device.ps1 `
  -Serial '<EXPLICIT_SERIAL>' `
  -ExpectedApi <API> `
  -ExpectedAbi '<ABI>' `
  -ExpectedUserIds @(<SORTED_USER_IDS>) `
  -HostRepository '<CLEAN_HOST_REPOSITORY>' `
  -PluginRepository '<CLEAN_PLUGIN_REPOSITORY>' `
  -ExpectedHostCommit '<HOST_COMMIT>' `
  -ExpectedPluginCommit '<PLUGIN_COMMIT>' `
  -FunctionalGate '<R2_E3_FUNCTIONAL_GATE_JSON>' `
  -FunctionalGateSha256 '<R2_E3_FUNCTIONAL_GATE_SHA256>' `
  -ObservationFixture '.\tools\tests\fixtures\u1-r2-device-observation-contract.json' `
  -ObservationFixtureSha256 '<FIXTURE_SHA256>' `
  -HostApk '<HOST_APK>' `
  -HostSha256 '<HOST_APK_SHA256>' `
  -HostTestApk '<HOST_ANDROID_TEST_APK>' `
  -HostTestSha256 '<HOST_ANDROID_TEST_APK_SHA256>' `
  -PluginApk '<PLUGIN_APK>' `
  -PluginSha256 '<PLUGIN_APK_SHA256>' `
  -ExpectedSignerSha256 '<SIGNER_CERT_SHA256>' `
  -AdbPath '<ADB_EXECUTABLE>' `
  -Aapt2Path '<AAPT2_EXECUTABLE>' `
  -ApkSignerPath '<APKSIGNER_EXECUTABLE>' `
  -Output '.\build\reports\python\u1\r2-binder-cpython-device-run-<UTC>-<SERIAL>-<NONCE>.json' `
  -ConfirmNoActiveSoak `
  -ConfirmDeviceMutation
```

The raw report is created once and never overwritten. Preserve its printed
SHA-256; the canonical verifier requires both the path and exact digest.

## Offline reproduction and canonical report

After the device transaction has fully restored the device, run the verifier
with the same immutable inputs plus the raw path/digest:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-u1-r2-binder-cpython-device.ps1 `
  -RawReport '<RAW_R2_REPORT>' `
  -RawReportSha256 '<RAW_R2_REPORT_SHA256>' `
  -ExpectedSerial '<EXPLICIT_SERIAL>' `
  -ExpectedApi <API> `
  -ExpectedAbi '<ABI>' `
  -ExpectedUserIds @(<SORTED_USER_IDS>) `
  -HostRepository '<CLEAN_HOST_REPOSITORY>' `
  -PluginRepository '<CLEAN_PLUGIN_REPOSITORY>' `
  -ExpectedHostCommit '<HOST_COMMIT>' `
  -ExpectedPluginCommit '<PLUGIN_COMMIT>' `
  -FunctionalGate '<R2_E3_FUNCTIONAL_GATE_JSON>' `
  -FunctionalGateSha256 '<R2_E3_FUNCTIONAL_GATE_SHA256>' `
  -ObservationFixture '.\tools\tests\fixtures\u1-r2-device-observation-contract.json' `
  -ObservationFixtureSha256 '<FIXTURE_SHA256>' `
  -HostApk '<HOST_APK>' `
  -HostSha256 '<HOST_APK_SHA256>' `
  -HostTestApk '<HOST_ANDROID_TEST_APK>' `
  -HostTestSha256 '<HOST_ANDROID_TEST_APK_SHA256>' `
  -PluginApk '<PLUGIN_APK>' `
  -PluginSha256 '<PLUGIN_APK_SHA256>' `
  -ExpectedSignerSha256 '<SIGNER_CERT_SHA256>' `
  -AdbPath '<ADB_EXECUTABLE>' `
  -Aapt2Path '<AAPT2_EXECUTABLE>' `
  -ApkSignerPath '<APKSIGNER_EXECUTABLE>'
```

The verifier performs no ADB operation. It rehashes the raw report, fixture,
gate, tools and APKs; rechecks clean repository identity, signer/package/ABI
metadata, every instrumentation class/method/argument/status/output digest,
restoration and downgraded claims; and atomically creates the canonical report
only if it does not already exist.

R2 E3 remains open unless that canonical report exists, says `PASS`, binds the
intended clean commits and exact artifacts, contains five passing observations
and proves restoration. Source tests, local CPython, Gradle builds, an E2.5
functional gate or an unverified raw JSON cannot substitute for it.
