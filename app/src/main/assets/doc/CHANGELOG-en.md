******

### Release history

******

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

# v0.5.0-alpha.6

###### 2026/08/25

* `Hint` Sixth current-tree alpha candidate; complete the AutoJs6 WakeActivity contract for first-time Plugin activation on OnePlus OPD2413 and similar OEMs without claiming a production signed candidate, beta, or publication
* `Fix` Declare `org.autojs.plugin.WAKE_ACTIVITY` and `org.autojs.plugin.action.WAKE` with a signature-protected immediately finishing NoDisplay Activity, allowing Plugin Center `ACTIVATE` to clear `stopped/notLaunched` and retry enablement automatically
* `Improvement` Reproduce and recover the original failure with `afca7b14c` debug Host and a matching-signer diagnostic Plugin, returning the startup probe result at `277 ms`; separately confirm that a signer mismatch fails closed as `PYTHON_RUNTIME_PROVIDER_UNTRUSTED`

# v0.5.0-alpha.5

###### 2026/08/25

* `Hint` Fifth current-tree alpha candidate; rebuild all three Host API release AAR files from exact clean `afca7b14c` with byte-identical payloads and refresh the provenance lock to that source without claiming a signed APK, the ten-item Android smoke, beta, or publication
* `Improvement` Run Host `verifyPythonReleaseApiDistributionGate` in an isolated worktree and pin AutoJs6 6.8.0/versionCode 5276, protocol 1.6, the source fingerprint, and the distribution-manifest SHA-256 with `dirty=false`

# v0.5.0-alpha.4

###### 2026/08/25

* `Hint` Fourth current-tree alpha candidate; M6 consolidates the unpublished 0.2/0.3/0.4 waypoints into one cumulative 0.5.0 train without claiming beta, stable release, signing, or publication
* `Feature` Add `tools/verify-m6-candidate.py` with explicit `--source-only` and `--full` profiles for clean Git/version/changelog/generated-document/AAR-lock checks plus portable tests, the R2 static gate, and an offline debug build
* `Improvement` Define one 10-item Android smoke checklist and the alpha → beta → 0.5.0 promotion sequence; the local gate performs no ADB, signing, tag, push, or publication operation

# v0.5.0-alpha.3

###### 2026/08/24

* `Hint` Third M5 current-tree alpha candidate; focused long-running and Host FIFO Android smokes pass on QV710AF65F, and measured startup keeps process retention out of scope without claiming publication or release
* `Improvement` Measure five fresh-process launches at 441/447/429/427/428 ms with five distinct Plugin PIDs; the all-sample median is 429 ms, the median excluding the first run is 428.5 ms, and the maximum is 447 ms
* `Improvement` Close process-prewarm evaluation below the 1000 ms threshold: retain per-execution process retirement and its state-isolation/cancellation semantics instead of adding a keep-process option

# v0.5.0-alpha.2

###### 2026/08/24

* `Hint` Second M5 current-tree alpha candidate; Host FIFO concurrency source and offline JVM/portable gates pass, but no Android concurrency smoke, true parallel CPython, prewarm, publication, or release claim is made
* `Feature` Admit concurrent Python launches through one fair Host FIFO owner plus at most 32 waiters before Provider discovery; queued Stop is interruptible and does not bind the Plugin, consume request timeout, or create a long-task foreground notification
* `Improvement` Keep a dispatched Provider binding for up to 3 seconds after session close to confirm process-generation retirement before FIFO handoff; protocol 1.6, all three AARs, and the Plugin single-session/no-provider-queue boundary remain unchanged

# v0.5.0-alpha.1

###### 2026/08/24

* `Hint` First M5 current-tree alpha candidate; protocol 1.6 foreground long-running source plus offline Host/Plugin JVM and portable gates pass, but no M5 Android smoke has run and publication, concurrency, and process prewarm are not claimed
* `Feature` Add project-level `executionMode=long-running` with no elapsed deadline, owned by a Host `specialUse` foreground service, persistent notification, and Stop action; scheduled, background/Intent, and developer launch surfaces reject without downgrade
* `Improvement` Emit ordered Provider heartbeats every 15 s and enforce Host leases of 2 min for start, 45 s for heartbeats, and an independent foreground-service lease; liveness loss and manual Stop fail closed through process-restart cancellation while bounded protocol 1.0-1.5 remains compatible

# v0.4.0-alpha.9

###### 2026/08/24

* `Hint` Ninth current-tree alpha candidate; close the M4 Path C native-package evaluation as `NOT_ADMITTED`, keep the embedded runtime `stdlib-only`, add no Pillow, NumPy, OpenCV, or transitive native payload, and make no new device-acceptance claim
* `Improvement` ADR 0004 records local `--no-index --find-links` dual-ABI offline debug builds: Pillow 11.0.0 adds 2,054,483 bytes to each APK, NumPy 1.26.2 adds 21,931,164 bytes, and all six candidate outputs pass `zipalign -c -P 16 4`
* `Improvement` Full-closure NDK 29 ELF audit rejects FreeType at `0x1000` on both ABIs and OpenBLAS/libgfortran at `0x1000` on x86_64; OpenCV has no official `cp313` Android wheel, and reopening requires reproducible NDK r28+ wheels plus 16 KiB public-engine acceptance

# v0.4.0-alpha.8

###### 2026/08/24

* `Hint` Eighth current-tree alpha candidate; close the M4 Path B build-time package evaluation as `NOT_ADMITTED`, keep the embedded runtime `stdlib-only`, add neither `requests` nor any candidate dependency, and make no new device-acceptance claim
* `Improvement` ADR 0003 records stdlib-only debug APK baselines of 23,709,688 bytes for arm64-v8a, 23,726,048 bytes for x86_64, and 34,622,039 bytes for universal; avoid a fabricated size delta without an audited offline wheelhouse, and require Gradle `--offline`, `--no-index`, `--require-hashes`, license/hash locks, three-APK size deltas, and dual ABI public-engine acceptance for future admission

# v0.4.0-alpha.7

###### 2026/08/24

* `Hint` Seventh M3 automation current-tree alpha candidate; the complete real-Settings workflow passed on the API 37 emulator, while publication, M4 Paths B/C, and a complete device matrix remain outside this claim
* `Feature` Add `m3_complete_automation`, a bounded real-Settings workflow using `app.launch`, `selector.find`, `selector.click`, and `images.capture_screen`, with strict PNG and destination-control containment assertions
* `Fix` Normalize platform accessibility bounds with `right < left` or `bottom < top` to anchored zero-area axes before Python serialization, while exact selector queries avoid unrelated tree nodes
* `Improvement` Pass the exported `RunIntentActivity` public project path on an API 37 emulator with a 1080x2424 PNG and SHA-256-verified artifact, then restore accessibility to 0/null and remove all exact test staging

# v0.4.0-alpha.6

###### 2026/08/24

* `Hint` Sixth M3 automation current-tree alpha candidate; configured Host OCR recognition passed on an eligible-service API 37 emulator and failed closed on an API 31 physical device without changing its accessibility services; richer OCR, publication, and a complete device matrix remain outside this claim
* `Feature` Add `autojs6.ocr.recognize(image)` for bounded PNG/JPEG bytes and an immutable ordered tuple of text lines from the configured Host OCR engine
* `Improvement` Reuse the 1 MiB PNG/JPEG upload in 24 KiB raw chunks with SHA-256 verification, select only an enabled, authorized, compatible Host OCR service, cap results at 256 lines, 4 KiB strict UTF-8 per line, and 48 KiB total, always release and zero buffers, and report stable `OCR_UNAVAILABLE` or `OCR_FAILED` failures

# v0.4.0-alpha.5

###### 2026/08/24

* `Hint` Fifth M3 automation current-tree alpha candidate; bounded template matching passed on an accessibility-enabled API 37 emulator and failed closed on an API 31 physical device without changing its accessibility services; OCR, publication, and a complete device matrix remain outside this claim
* `Feature` Add `autojs6.images.find_image(template, *, region=None, threshold=0)` for PNG/JPEG bytes, an optional bounded region, and a top-left coordinate-or-`None` result
* `Improvement` Upload one execution-local template up to 1 MiB in 24 KiB raw chunks with SHA-256 verification, decode at most 2048 pixels per side, scan deterministically in row-major order under `autojs6-python-image-match-v1`, use exact-alpha pixels as participants and other pixels as wildcards, require no OpenCV, always release and zero buffers, and retry only Android's 333 ms screenshot throttle after a bounded 350 ms wait

# v0.4.0-alpha.4

###### 2026/08/24

* `Hint` Fourth M3 automation current-tree alpha candidate; bounded screen color search passed on an accessibility-enabled API 37 emulator and failed closed on an API 31 physical device without changing its accessibility services; template image matching, OCR, publication, and a complete device matrix remain outside this claim
* `Feature` Add `autojs6.images.find_color(color, *, region=None, threshold=0)` for strict RGB integers or `#RRGGBB` text, an optional bounded region, and a coordinate-or-`None` result
* `Improvement` Capture one fresh Android 11+ accessibility screenshot per call, scan it in deterministic row-major order with a per-channel threshold from 0 through 255, validate exact `autojs6-python-color-match-v1`, and transfer no image bytes or handles to Python

# v0.4.0-alpha.3

###### 2026/08/24

* `Hint` Third M3 automation current-tree alpha candidate; the complete bounded Android 11+ screen-capture path passed focused acceptance on an accessibility-enabled API 37 emulator, and fail-closed passed on an API 31 physical device without changing its accessibility services; image/color matching, OCR, publication, and a complete device matrix remain outside this claim
* `Feature` Add `autojs6.images.capture_screen`, returning verified PNG/JPEG encoded bytes or atomically writing and publishing an execution output artifact
* `Improvement` Retain at most 1 capture per execution, transfer 32 KiB raw chunks, and cap encoded data at 4 MiB; Python verifies order, EOF, SHA-256, and format signatures and always releases, while the Host zeros on replacement/release/terminal and reports stable failures without enabling services or opening settings

# v0.4.0-alpha.2

###### 2026/08/24

* `Hint` Second M3 automation current-tree alpha candidate; the full bounded selector/UI-tree path passed focused acceptance on an accessibility-enabled API 37 emulator, and fail-closed passed on an API 31 physical device without changing its accessibility services; screenshots, OCR, publication, and a complete device matrix remain outside this claim
* `Feature` Add live `autojs6.selector.snapshot/find/click/set_text` APIs for detached accessibility-tree data, AND-composed first-match queries, and explicit actions through opaque execution-local node references
* `Improvement` Bound snapshot nodes, depth, payload and node text, selector scan size, query/set text and retained nodes; report incomplete scans as `SELECTOR_SCAN_LIMIT_EXCEEDED`, stale references as `STALE_NODE`, and unavailable accessibility as `CapabilityUnavailableError` without opening settings

# v0.4.0-alpha.1

###### 2026/08/23

* `Hint` First M3 automation current-tree alpha candidate; bounded coordinate/global actions passed focused acceptance on an accessibility-enabled API 37 emulator and fail-closed passed on an API 31 physical device without changing its accessibility services, while selector/UI-tree, screenshots, OCR, publication, and a complete device matrix remain outside this claim
* `Feature` Add live `autojs6.automator.click/long_click/press/swipe/back/home` APIs through Host accessibility, returning the actual boolean dispatch result
* `Improvement` Require strict non-boolean integer coordinates from 0 through 1000000 and press/swipe durations from 1 through 4000 ms; unavailable Host accessibility raises `CapabilityUnavailableError` without opening settings

# v0.3.0-alpha.6

###### 2026/08/23

* `Hint` First M4 current-tree alpha candidate; the project-local pure-Python dependency path passed focused dual-device acceptance, while later M3/M4 batches, publication, and a complete device matrix remain outside this claim
* `Feature` Support project-local pure-Python packages and `.dist-info` metadata from admitted project roots, with a reproducible pinned `requests` example and no runtime installer
* `Improvement` Raise project workspace limits to 64 MiB compressed, 8192 file entries, and 128 MiB extracted, and match the snapshot's actual three-dimensional requirement against Provider capabilities before dispatch; missing imports remain `ModuleNotFoundError` without online pip or engine fallback

# v0.3.0-alpha.5

###### 2026/08/23

* `Hint` Fifth M3 current-tree alpha candidate; the bounded Host-engines portion of the second capability slice passed focused dual-device acceptance, while later capabilities, publication, and a complete device matrix remain outside this claim
* `Feature` Add live `autojs6.engines.current/run/stop_self` APIs for path-free current-engine metadata, asynchronous non-Python Host child-script launch, and deterministic self-stop
* `Improvement` Accept only normalized execution-root-relative child paths and at most 16 successful launches per execution; fail nested Python with stable `NESTED_PYTHON_NOT_ALLOWED`, while `stop_self` cancels through provider-process restart

# v0.3.0-alpha.4

###### 2026/08/23

* `Hint` Fourth M3 current-tree alpha candidate; foreground Host dialogs passed focused dual-device acceptance, while engines, later capabilities, publication, and a complete device matrix remain outside this claim
* `Feature` Add foreground-only `autojs6.dialogs.alert/confirm/prompt/select` APIs with typed acknowledgement, confirmation, nullable prompt text, and zero-based nullable selection results
* `Improvement` Bound dialog titles, content, replies, and items; serialize one Host-owned dialog at a time; and fail background launches closed with stable `INTERACTIVE_NOT_ALLOWED` without opening UI

# v0.3.0-alpha.3

###### 2026/08/23

* `Hint` Third M3 current-tree alpha candidate; the bounded Host-files portion of the second capability slice passed focused dual-device acceptance, while dialogs, engines, later capabilities, publication, and a complete device matrix remain outside this claim
* `Feature` Add live `autojs6.files.read_text/write_text/exists/is_file/is_dir/list` APIs for bounded UTF-8 text access within the current project root or standalone script directory
* `Improvement` Reject unsafe or escaping paths, cap text and direct listings, return stable file errors, and keep the live Host root distinct from the frozen Plugin workspace snapshot

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
