# Supply-chain lock workflow

No command in this file is current evidence. The protected-device soak has been
released, but Gradle work must still be serialized with the other Codex
processes. Before every Gradle invocation, poll for another active Gradle task
for up to nine minutes and do not start this build concurrently.

## Current fail-closed states

`python-runtime.lock` format 2 has two admitted states:

- `DEFERRED`: source/static scaffolding may pass, but `app/build.gradle.kts`
  refuses ordinary Gradle configuration. A narrow metadata-bootstrap window is
  described below; it is not build or release admission.
- `RESOLVED`: `runtime.artifacts.count` must be positive and every numbered
  artifact must have a coordinate, basename-only file name, and lowercase
  SHA-256. The canonical inventory digest must also match.

`gradle-wrapper.lock` independently locks the executable wrapper JAR. The
official Gradle 9.5.0 bin checksum was fetched separately from
`https://services.gradle.org/distributions/gradle-9.5.0-bin.zip.sha256` and was
`553c78f50dafcd54d65b9a444649057857469edf836431389695608536d6b746`.
Only after the 140,319,124-byte distribution matched that checksum was
`gradle-9.5.0/lib/plugins/gradle-wrapper-main-9.5.0.jar` opened. That container
has SHA-256
`11954fe51c5f8d56321f694ebb2aec206c3871eab57e0bef4465b9c281003982`;
its embedded 48,462-byte `gradle-wrapper.jar` has SHA-256
`497c8c2a7e5031f6aa847f88104aa80a93532ec32ee17bdb8d1d2f67a194a9c7`.
The checked-in JAR now matches those bytes and the wrapper state is `READY` with
provenance `OFFICIAL_GRADLE_9_5_0_DISTRIBUTION_EMBEDDED_WRAPPER`.

Any wrapper or distribution change returns this admission to `BLOCKED` until
the official checksum, source container/entry, expected hash and observed hash
are independently recorded and revalidated. Never relabel a wrapper from a
different distribution version.

`release-identity.lock` independently freezes the host and plugin package
names, the exact standard release-keystore byte SHA-256, and the corresponding
release-certificate SHA-256. Gradle release signing is ready only when the
configured keystore bytes match this lock. The R6 source gate rejects a
different keystore and any host-AAR lock whose Host HEAD is marked dirty or is
missing its explicit clean-source headers. The RC provenance producer requires
the host APK and all three plugin APK outputs to have exactly one signer, equal
to the pinned certificate, and embeds the identity-lock file record in its
report. No signing password or private-key material belongs in this lock.

## Runtime artifact inventory

After an explicitly reviewed dependency-resolution bootstrap, replace the
runtime `DEFERRED` state with entries like:

```properties
runtime.artifacts.state=RESOLVED
runtime.artifacts.count=2
runtime.artifact.000.coordinate=com.example:artifact-a:1.0
runtime.artifact.000.file=artifact-a-1.0.jar
runtime.artifact.000.sha256=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
runtime.artifact.001.coordinate=com.example:artifact-b:1.0
runtime.artifact.001.file=artifact-b-1.0.jar
runtime.artifact.001.sha256=abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789
runtime.artifacts.inventory.sha256=<canonical-inventory-sha256>
```

Number entries from `000` with no gaps. The canonical inventory is UTF-8 text
containing one line per entry in numeric order:

```text
000|com.example:artifact-a:1.0|artifact-a-1.0.jar|0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef\n
001|com.example:artifact-b:1.0|artifact-b-1.0.jar|abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789\n
```

The SHA-256 of those exact bytes is
`runtime.artifacts.inventory.sha256`. The static gate and Gradle configuration
both accept a correctly formed future `RESOLVED` inventory; neither hard-codes
the old unresolved marker.

## Reviewed metadata cycle

Only after the wrapper is `READY`, host release AARs are staged and hash-pinned,
and the runtime inventory bootstrap is explicitly authorized, resolve the exact
configurations used by the R2 build in one review cycle:

```powershell
.\gradlew.bat --console=plain --no-daemon --no-parallel --max-workers=2 `
  -Pautojs.python.runtime.lock.bootstrap=true `
  --write-locks --write-verification-metadata sha256 `
  :app:testDebugUnitTest :app:lintDebug :app:assembleDebug
```

The `DEFERRED` exception is admitted only when all of these inputs are present
at the same time:

- the bootstrap property is exactly `true`;
- the requested task set is exactly the three fully qualified debug tasks shown
  above, with no duplicate or excluded task;
- Gradle is in full `--write-locks` mode, not `--update-locks` mode;
- the verification-metadata write algorithm list is exactly `sha256`; and
- the invocation is not a dry run.

Any ordinary, arbitrary, release, bundle, install, connected-test, or device
task remains blocked while the inventory is `DEFERRED`. Missing either write
flag also remains blocked. This exception lets Gradle create review inputs; it
does not make the generated metadata trusted and does not admit an APK.

The completed bootstrap established an important boundary: `app/gradle.lockfile`
contains the ordinary Gradle dependencies, but contains no
`com.chaquo.python*` coordinate. Chaquopy's plugin resolves the packaged runtime
separately. The candidate tool therefore requires a non-empty generated Gradle
lockfile and records its SHA-256 as ordinary-lock evidence, while rejecting any
attempt to treat that file as the runtime inventory source.

The runtime candidate is an exact nine-file contract sourced from
`gradle/verification-metadata.xml` and matching cache bytes:

- `com.chaquo.python:target:3.13.9-0`: the `arm64-v8a` target ZIP, stdlib-pyc
  ZIP, and `x86_64` target ZIP;
- `com.chaquo.python.runtime:bootstrap:17.0.0`: the Python 3.13 `.imy`;
- `com.chaquo.python.runtime:chaquopy:17.0.0`: one `.so` for each admitted ABI;
- `com.chaquo.python.runtime:chaquopy_java:17.0.0`: the runtime JAR; and
- `com.chaquo.python.runtime:libchaquopy_java:17.0.0`: one `.so` for each
  admitted ABI.

The only admitted ABIs are `arm64-v8a` and `x86_64`. The Gradle build-plugin
components are explicitly filtered, as are `.pom` and `.module` metadata
artifacts. An unknown component/version, extra runtime binary or ABI, missing
expected file, ambiguous identity, absent verification SHA-256, or mismatch
against actual cache bytes fails closed.

Generate a review candidate from the lockfile, verification metadata, and both
exact Chaquopy cache groups. The script reads only and writes the candidate to
standard output:

```powershell
$moduleCache = "$env:GRADLE_USER_HOME\caches\modules-2\files-2.1"
python .\tools\runtime_lock_inventory_candidate.py `
  --artifact-root "$moduleCache\com.chaquo.python" `
  --artifact-root "$moduleCache\com.chaquo.python.runtime" `
  --format json
```

The default inputs are `app/gradle.lockfile` and
`gradle/verification-metadata.xml`. Exact `--artifact <path>` arguments may be
used instead of, or in addition to, roots. The JSON output records both input
file hashes, the exact runtime contract, coordinate, basename, verified byte
SHA-256, canonical inventory text and canonical inventory SHA-256. Properties
output remains available with `--format properties`. Both formats are visibly
marked `REVIEW_CANDIDATE_ONLY`/`REVIEW CANDIDATE ONLY`.
The script has no file-write or process-launch path and never edits
`locks/python-runtime.lock`.

If a reviewer captures stdout to a separate candidate file, re-check that file
against the same three inputs with:

```powershell
$moduleCache = "$env:GRADLE_USER_HOME\caches\modules-2\files-2.1"
python .\tools\runtime_lock_inventory_candidate.py `
  --artifact-root "$moduleCache\com.chaquo.python" `
  --artifact-root "$moduleCache\com.chaquo.python.runtime" `
  --format json `
  --verify-candidate <review-candidate-path>
```

Before accepting it:

1. Review `app/gradle.lockfile` as ordinary dependency-lock evidence and
   `gradle/verification-metadata.xml` as the plugin-managed runtime hash source.
2. Independently verify the Gradle, Chaquopy, CPython and host-AAR provenance and SHA-256 values.
3. Review and re-verify the generated candidate; do not copy it automatically.
4. Manually record every resolved Chaquopy/CPython artifact plus the canonical
   inventory digest in `python-runtime.lock`; do not use one aggregate artifact
   guess.
5. Remove the bootstrap property and both write flags, then run the named gates
   again. Only ordinary configuration against the reviewed `RESOLVED` lock can
   become build evidence.

Strict dependency locking intentionally makes an ordinary dependency resolution fail while lock
state is absent. Generated checksums are candidates for review, not trust by themselves.
