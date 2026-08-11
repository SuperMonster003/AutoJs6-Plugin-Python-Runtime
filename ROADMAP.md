# Python Runtime Plugin Roadmap

This roadmap separates filesystem/static progress from Gradle, Android, Binder, and device evidence. A checked static item is not runtime acceptance.

## R2-A: independent repository and frozen boundary

- [x] Create the independent sibling repository scaffold and release identity
- [x] Freeze application ID/namespace to `io.github.supermonster003.autojs6.plugin.python.runtime`
- [x] Freeze Binder action to `org.autojs.plugin.python.RUNTIME`
- [x] Freeze runtime process to `:python_runtime`
- [x] Freeze provider ID to `org.autojs.python.runtime.cpython`
- [x] Freeze SDK range to min/target/compile `24/36/36`
- [x] Pin Android Gradle Plugin `9.2.1`, within Chaquopy 17's documented support range
- [x] Freeze Chaquopy `17.0.0`, Python line `3.13`, and expected CPython `3.13.9`
- [x] Restrict packaged ABIs to `arm64-v8a` and `x86_64`
- [x] Declare stdlib-only packaging with zero third-party Python packages
- [x] Reject online `pip` as an R2 runtime capability
- [x] Add fail-closed release-AAR staging and SHA-256 lock template
- [x] Pin the Gradle 9.5.0 distribution archive SHA-256 and restrict dependency repositories to Google/Maven Central
- [x] Detect and record the checked-in Gradle 8.14 wrapper JAR mixed with a Gradle 9.5.0 distribution as a provenance blocker
- [x] Replace that mixed-version wrapper with the embedded wrapper from a checksum-verified official Gradle 9.5.0 bin distribution and promote `locks/gradle-wrapper.lock` to `READY`
- [x] Enable strict dependency locking so an unresolved configuration cannot become acceptance evidence
- [x] Add a filesystem-only static gate
- [x] Record a provisional Chaquopy-vs-official-CPython ADR and its promotion blockers
- [x] Add deterministic OpenCC-style README/changelog generation for exactly 10 locales

## R2-B: runtime provider implementation

The provider now has ordinary (non-bootstrap) Android compilation plus focused
JVM evidence. Device execution remains separate and pending.

- [x] Implement exported `PythonRuntimePluginService` in `:python_runtime`
- [x] Accept explicit component binding where the incoming action may be null
- [x] Revalidate Binder caller UID, installed host package, and exact current signer set at every entry point
- [x] Return provider info and conservative capabilities through protocol 1.0-1.1 tagged wire
- [x] Atomically adopt complete Binder receiver PFD copies, preserving reliable-pipe error channels
- [x] Enforce one active session and zero provider-side queueing
- [x] Stage SOURCE into a private in-memory snapshot with exact-length, EOF, and SHA-256 validation
- [x] Enable verified project workspaces with 16 MiB archive / 1024 entry / 32 MiB expansion ceilings; keep stdin disabled
- [x] Execute one source payload with `__name__ == "__main__"`
- [x] Buffer bounded stdout/stderr order, then use shared credits for delivery; execution-time streaming backpressure is not claimed
- [x] Serialize `onStarted`, output, terminal, and close ordering through one session callback arbiter
- [x] Encode `SystemExit`, syntax/runtime exceptions, and structured traceback outcomes
- [x] Make `cancel` and `close` idempotent in the source state machine
- [x] Declare cooperative cancellation unsupported and use `PROCESS_RESTART_ONLY`
- [x] Retire the dedicated process on cancel, timeout, callback death, or post-terminal close
- [x] Avoid passing Context, Binder, host runtime objects, or callback sinks into script globals
- [x] Zero the source snapshot and close descriptors on every modeled terminal/close path
- [x] Add local CPython bootstrap tests for output order, chunk/byte limits, `SystemExit`, and exceptions
- [x] Compile the provider with the audited `RESOLVED` lock under an ordinary Gradle invocation
- [x] Run 5 focused JVM suites / 23 tests for metadata, the single-active/retiring gate, callback FIFO/drain, process retirement, credits, quotas, and single-terminal policy
- [ ] Prove the Binder-wrapped provider state machine on Android
- [ ] Prove cancel/timeout/native hangs through Binder death and clean rebind without replay
- [ ] Freeze a versioned admission-abandon timeout before adding any provider-side unstarted-session lease

## R2-C: host and supply-chain admission

- [x] Replace the self-locking `UNRESOLVED` contract with format-2 `DEFERRED`/`RESOLVED` states and a canonical per-artifact inventory digest
- [x] Keep `DEFERRED` acceptable only to the filesystem/static scaffold; Gradle configuration fails closed until a real `RESOLVED` inventory is audited
- [x] Record and clear `WRAPPER_JAR_VERSION_8_14_WITH_DISTRIBUTION_9_5_0` by replacing—not relabeling—the JAR
- [x] Record the official Gradle 9.5.0 distribution, wrapper-main container, embedded entry, expected/observed SHA-256 and provenance
- [x] Add a narrowly scoped `DEFERRED` metadata-bootstrap window requiring an explicit property, the exact three debug tasks, full lock writing, and SHA-256 verification-metadata writing
- [x] Reject arbitrary, release, device/connected, excluded, update-locks, missing-write-flag, and dry-run bootstrap requests in the static policy self-test
- [x] Correct the runtime evidence boundary from bootstrap results: `app/gradle.lockfile` proves ordinary dependency locking but does not contain Chaquopy's plugin-managed runtime coordinates
- [x] Add a read-only candidate generator/verifier for the exact five runtime components, Python `3.13.9-0`, Chaquopy `17.0.0`, ABIs `arm64-v8a`/`x86_64`, and nine packaged files; filter build-plugin/POM/module metadata and reject missing, extra, ambiguous, or byte/hash-mismatched input
- [x] Produce local release `protocol-wire-api.aar` and `python-runtime-api.aar` from the host (not remotely published)
- [x] Stage the two manifest-matched release AARs separately from debug artifacts
- [x] Record their SHA-256 values in `locks/host-api-aars.lock`
- [x] Capture resolved Maven dependency locking and SHA-256 verification metadata
- [x] Verify all three merged debug APK manifests request zero Android permissions
- [x] Capture Chaquopy/CPython attribution, upstream source pointers, MPL source access, and package the matching root/asset copies of `THIRD_PARTY_NOTICES.md`
- [x] Verify no 32-bit/third ABI or third-party wheel is packaged; record that Chaquopy assets keep both allowed 64-bit ABIs inside each split APK
- [ ] After logical commits, set `VERSION_BUILD` to the repository commit count and verify a clean release tree
- [x] Document that Chaquopy Java interoperability prevents a strong Python sandbox claim
- [x] Add the R6 role-based CPython runtime maintenance policy in `docs/maintenance/CPYTHON_RUNTIME_POLICY.md` for upgrades, CVE/EOL triage, lock regeneration, rollback, and trusted-local-script boundaries

## Host R3-S dependency checkpoint

This is a cross-repository, fail-closed precursor and is not an R2 or R3 PASS:

- [x] The host contains an uncompiled `PythonLaunchBoundaryPolicy` and routes
  shared `ScriptLaunchSourceFactory` construction paths through it.
- [x] The current boundary only rejects `.py`, `.pyc`, and unsupported
  identifiable Python-looking URI/MIME/display-name launches before legacy
  dispatch; canonical targets and editor temporary-file origins are rechecked.
- [x] The host still has no `PythonScriptSource`, `PythonFileSource`,
  `PythonPluginScriptEngine`, production runtime discovery/binding, engine
  registration, or Python execution route.
- [ ] Compile and execute the host R3-S tests after the protected soak is
  explicitly released. This remains receipt-free and cannot promote R2 or R3.

## R2-D: protected-soak device evidence contract

These checks make the deferred state machine-readable; they do not authorize or
perform a device run:

- [x] Add `tools/device/deferred-device-plan-v1.json` with status `DEFERRED`,
  execution authorization false, current claim `NOT_RUN`, no selected serial,
  and `QV710AF65F` in the protected serial set.
- [x] Require a future exact serial, forbid environment/automatic/fallback
  selection, and require every future ADB argument template to begin with the
  exact `adb -s ${serial}` prefix.
- [x] Add a read-only, fail-closed plan validator with no subprocess, runner,
  device-discovery, evidence-write, or receipt-generation capability.
- [x] Add ten local contract tests for protected-serial removal, premature soak
  completion, serial selection, fallback, bare ADB, Gradle/connected tokens,
  execution authorization, PASS/receipt claims, and duplicate JSON keys.
- [x] Validate the canonical deferred plan and the ten tests locally. This is
  Python/filesystem evidence only and is not Android or device acceptance.
- [ ] After explicit soak completion confirmation, replace this plan-only
  topology with a separately reviewed exact-serial runner and evidence schema;
  keep execution disabled until its negative tests and restoration policy pass.

## Soak completion confirmed; build admission still blocked - 2026-08-10

- [x] User confirmed that the `QV710AF65F` soak completed and Gradle/ADB work may resume
- [x] Preserve the rule that no Gradle task starts concurrently with another Codex Gradle task; poll for up to nine minutes before each invocation
- [x] Wrapper provenance blocker cleared using the checksum-verified official Gradle 9.5.0 distribution
- [x] Promote the runtime supply lock from source-only `DEFERRED` to an audited per-artifact `RESOLVED` inventory
- [x] Remove the runtime-lock bootstrap self-lock without opening ordinary, release, or device configuration
- [x] Run the single serialized metadata-bootstrap invocation after host release AAR admission and capture `app/gradle.lockfile` plus `gradle/verification-metadata.xml`; this subtask consumed those files read-only and did not rerun Gradle
- [x] Reproduce the exact nine-file review candidate from current verification metadata and cache bytes: canonical inventory SHA-256 `cc4148718389c17e7756e9d72ec8264b5d0e678f5328a613ac09f7d0c996c180`; this is candidate evidence, not trusted-lock promotion
- [x] Independently review the exact nine-file read-only inventory candidate and both input-file hashes
- [x] Manually promote the runtime supply lock after review, then rerun without the bootstrap property or write flags
- [x] Run 5 JVM suites / 23 unit tests (0 failures/errors/skips) and lint (0 errors, 35 warnings)
- [x] Assemble three debug APK variants; release APK assembly remains pending
- [x] Inspect debug APK manifests, native libraries, allowed ABIs, v2 signatures, ZIP alignment, and all ELF LOAD segments for 16 KB compatibility
- [x] Run seven bounded current-tree host/plugin Binder/PFD/CPython diagnostics covering eleven exact cases on the explicitly released `QV710AF65F`; this is one matrix cell, not acceptance
- [ ] Run API 24-36, arm64-v8a, and x86_64 acceptance matrix
- [x] Run a bounded same-signer/different-UID provider-entry rejection
  diagnostic through a successful signature-permission bind
- [ ] Test a different-signer caller, alternate-UID session-handle relay, plus
  plugin missing/disabled/update/uninstall and Binder death races
- [x] Rerun timeout, infinite loop, process restart, and cancellation on the
  current source-staging build
- [x] Prove typed timeout, process death, changed generation, and exact finite
  recovery for `os.read` blocking I/O and `hashlib.pbkdf2_hmac` native work
- [x] Prove reliable-pipe `closeWithError` survives receiver ownership and
  rejects otherwise valid bytes, then prove a fresh reliable-pipe recovery
- [x] Exercise stdout/stderr sequence/credits and the bounded output limit;
  stress and exhaustion coverage remains pending
- [x] Record exact hashes, Android users `[0, 10]`, and restoration evidence for
  all seven bounded diagnostics; the formal R2 receipt remains absent

The user explicitly confirmed completion of the protected soak on 2026-08-10.
This releases the earlier blanket Gradle/ADB prohibition, but it does not clear
supply-chain blockers or authorize overlapping Gradle work. Before every Gradle
invocation, inspect the active processes for another Codex-owned Gradle task. If
one exists, poll for up to nine minutes and do not start this build concurrently.
The current static scaffold remains intentionally receipt-free.

### Current R2 build evidence — 2026-08-10

- Ordinary command (no bootstrap property and no lock-write flags):
  `:app:testDebugUnitTest :app:lintDebug :app:assembleDebug` — PASS.
- Runtime inventory: 9 files, canonical SHA-256
  `cc4148718389c17e7756e9d72ec8264b5d0e678f5328a613ac09f7d0c996c180`.
- Current staged host release API AAR lock (refreshed 2026-08-11; downstream
  APK hashes below retain their separately dated evidence identity): protocol
  `e044dd3cc9bed84e844174e0963b57a1f67902cf021ccb42d1031d3511ce46da`
  and Python runtime
  `900e9c74db33340b1f1aa155d8e8454708338ee7ca763d1caafca33431ce42a4`.
- JVM evidence: 5 suites / 23 tests / 0 failures / 0 errors / 0 skipped.
- Lint evidence: 0 errors / 35 warnings.
- Debug APK SHA-256 after source-staging / deferred-`onStarted` hardening: arm64-v8a
  `d1a6c99796da5fdea2de758ad7b396717ba4456919e37d7901a14f7611ea1764`,
  x86_64
  `5fca85eb5328f78dbbdb61d9b86767339a4ab46721f7b4c9445f24528706167d`,
  universal
  `e28c3d6967946e3792c1bfabf667b12718fb47d0c3a604bdbd4863def59ed558`.
- Offline APK scope passed: v2 signature, zero requested permissions, one
  protected exported runtime service, only the two allowed 64-bit ABIs, no
  third-party wheels, and 16 KB LOAD/ZIP alignment. Both split APKs still
  contain both allowed ABIs inside Chaquopy asset archives, so strict
  whole-ZIP single-ABI purity is not claimed.
- This evidence proves build/JVM/static packaging only. It does not prove
  Binder execution, CPython startup, cancellation, rebind, no-replay, or R2
  device acceptance; no R2 PASS receipt exists.

### Current real-plugin device diagnostics — 2026-08-10

- Exact serial: `QV710AF65F` (API 31, `arm64-v8a`).
- Host APK SHA-256:
  `102ca6c52bfab8906716aaafe8935f5a446a51f7e32a001b9928bd56322b3bb1`.
- Host androidTest APK SHA-256:
  `5bfe88f95728d4c0593fb9abfa23cc24c01014d1f2059a9ff6ae0bf4bcdf9b1f`.
- Plugin arm64 APK SHA-256:
  `d1a6c99796da5fdea2de758ad7b396717ba4456919e37d7901a14f7611ea1764`.
- Seven current-tree runners passed eleven exact cases with zero skips: positive
  finite execution; four outcome cases (`SystemExit(23)`, syntax/runtime
  traceback, and output limit); cancel/death/rebind; timeout/death/rebind;
  reliable-pipe producer error plus recovery; and never-ending-pipe staging
  timeout plus recovery; plus `os.read` blocking-pipe and
  `hashlib.pbkdf2_hmac` native-work timeout/death/rebind cases.
- The bounded cell verified action-null exact binding, PFD/SHA-256 input,
  packaged CPython 3.13.9, callback UID, stdout/stderr sequencing and credits,
  structured failures, typed cancellation/timeout before old Binder death,
  changed runtime generations, and exact finite recovery without
  diagnostic-harness replay.
- Each runner froze Android users `[0, 10]`, restored the three initially absent
  packages, and verified absence across both users, retained/global records,
  and Python-scope processes. Evidence is preserved by the host under
  `build/reports/python/r2-partial-testsha-5bfe88f9/01-positive.json` through
  `07-blocking-native.json`.
- Every result reports `PARTIAL_DIAGNOSTIC`,
  `acceptanceReceiptWritten=false`, and `r2DeviceAcceptance=false`. These seven
  runners cannot create or substitute for the formal R2 gate receipt.
- Remaining formal R2 work includes a different-signer caller and alternate-UID
  session-handle relay, provider update/disable/uninstall/death races,
  FD/thread/snapshot stress, fresh 8-hour and 24-hour soaks, API 24-36 plus
  `arm64-v8a`/`x86_64`, production-host after-dispatch no-replay, and the
  official-CPython/Chaquopy threat-model and maintenance decision.
- `build/reports/python/r2-runtime-poc-gate.json` remains absent. R2 is
  incomplete and no R2 PASS is claimed.

### R2-I1 same-signer different-UID diagnostic — 2026-08-10

- Exact serial: `QV710AF65F` (API 31, `arm64-v8a`, frozen Android users
  `[0, 10]`).
- Consumer target APK SHA-256:
  `0dbe79ab844a1cfc9531e9b61c50150baf36f38dba4d58617b0264ccf0458c64`.
- Consumer androidTest APK SHA-256:
  `4d91301f7d34ab4d11d7a5b17d5dbe43bc494e8161045041bf767b42defdc87c`.
- Host APK SHA-256:
  `102ca6c52bfab8906716aaafe8935f5a446a51f7e32a001b9928bd56322b3bb1`.
- Plugin arm64 APK SHA-256:
  `d1a6c99796da5fdea2de758ad7b396717ba4456919e37d7901a14f7611ea1764`.
- The signature-protected provider bind succeeded and the consumer target UID
  was distinct from the host UID. `getRuntimeInfo`, `getCapabilities`, and
  `openSession` each threw a synchronous `SecurityException`; no callback or
  provider session was dispatched.
- All four initially absent packages were restored absent across users
  `[0, 10]` and global/retained package records.
- Host evidence:
  `build/reports/python/r2-identity-testsha-4d91301f/01-same-signer-different-uid.json`.

The result is `PARTIAL_DIAGNOSTIC` and covers only the same-signer/different-UID
provider-entry boundary. Different-signer rejection and alternate-UID
session-handle relay remain untested. It does not change the current
seven-runner/eleven-case execution bundle, cannot create an acceptance receipt,
and does not complete R2.

Historical immediately preceding current-tree checkpoint:

- Host APK SHA-256:
  `102ca6c52bfab8906716aaafe8935f5a446a51f7e32a001b9928bd56322b3bb1`.
- Host androidTest APK SHA-256:
  `2b3735d450641e3dab22c8633c01fdff8bbbbb2e0a8e220bb51916c638ac8b92`.
- Plugin arm64 APK SHA-256:
  `d1a6c99796da5fdea2de758ad7b396717ba4456919e37d7901a14f7611ea1764`.
- The host directory `build/reports/python/r2-partial-testsha-2b3735d4/`
  preserves the superseded six-runner/nine-case partial checkpoint. It is
  historical, not current, and does not cover the two blocking/native cases.

## Strict post-soak execution queue

After that explicit confirmation, execute in this order:

1. Freeze and record exact host/plugin revisions; confirm that no R2 or R3 PASS
   receipt exists for the unvalidated trees. Before every Gradle step below,
   poll for up to nine minutes when another Codex Gradle task is active.
2. Run the host R0 gate, R1 Android harness compile gate, and R1 aggregate gate,
   in that order and without any connected/managed-device Gradle task.
3. Produce host **release** protocol AARs, their manifest, and SHA-256 values;
   then complete the R1 fixture set and pass the exact-serial R1 device gate with
   preflight, package-state snapshot, and verified restoration.
4. Stage only the manifest-matched release AARs here. Revalidate the checked-in
   official Gradle-9.5.0 wrapper and its `READY` provenance lock, then resolve and review strict dependency
   locks, the per-artifact runtime inventory, and verification metadata. Complete logical commits, set
   `VERSION_BUILD` to the intended post-version-commit count, commit it, and
   verify the resulting count and clean tree before acceptance builds.
5. Compile and test the provider, run lint, and assemble debug/release APKs.
   Compilation or assembly alone is not CPython or device acceptance.
6. Inspect the merged manifest/permissions, exact Python version, ABI contents,
   every ELF/native wheel, artifact hashes, and 16 KB page compatibility.
7. With exact serials only, run every declared API/ABI matrix cell for real
   Binder/PFD/UID/signer/death, reliable-pipe error propagation, output limits,
   timeout/cancel/process retirement, clean rebind, and no replay. Snapshot and
   verify restoration after every cell; a single physical-device result is only
   one cell.
8. Create `build/reports/python/r2-runtime-poc-gate.json` only after all upstream
   build, supply-chain, Android, CPython, device-matrix, and restoration checks
   pass. A failure leaves that receipt absent and does not claim R2 PASS.
9. Return the receipt and exact plugin APK hash to the host. Only then may the
   host activate R3 engine registration/binding/execution and run its current-tree
   R3 gate; the earlier fail-closed R3-S source is not activation authority.

Any change to source, locks, AARs, APKs, signers, device images, or the declared
matrix invalidates downstream evidence. No old, diagnostic, or single-cell
artifact may be relabeled as the R2 receipt.
