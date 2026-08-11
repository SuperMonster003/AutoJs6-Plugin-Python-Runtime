# CPython Runtime Maintenance Policy

Status: R6 release-baseline policy. It defines ownership and the minimum
maintenance path; it is not a release receipt or a claim that Python code is
sandboxed.

## Ownership

Every maintained release line must name people for these roles in its release
record. One person may hold more than one role, but an unassigned role blocks a
stable release.

- **Runtime owner**: tracks the selected Chaquopy and CPython lines, evaluates
  upgrades and end-of-life, and owns runtime behavior regressions.
- **Security owner**: triages relevant CVEs and advisories, records exposure and
  mitigations, and can require the runtime channel to remain disabled.
- **Release owner**: rebuilds and reviews locks, verifies notices and source
  revision availability, and records the exact APK, signer, version and evidence.

## Supported baseline and source of truth

The current baseline is Chaquopy 17.0.0 with CPython 3.13.9, stdlib only, for
`arm64-v8a` and `x86_64`. `locks/python-runtime.lock` is the canonical artifact
inventory; `gradle/verification-metadata.xml` supplies dependency checksums, and
`docs/adr/0001-python-runtime-selection.md` records why this runtime was chosen.
The version strings in prose are descriptive and must not override those files.

## Security, CVE and end-of-life handling

The security owner reviews CPython security announcements, Chaquopy release
notes/advisories, and repository dependency alerts before each stable release
and periodically while that release line is supported. Each relevant report is
classified as affected, not affected, or still investigating, with the runtime
version and rationale recorded.

An actively exploited issue, or a critical issue that crosses the Python/Java
bridge or plugin UID boundary, keeps the candidate channel disabled and pauses
distribution until it is patched or explicitly mitigated. Lower-severity issues
must be assigned to a maintenance release with a recorded disposition; silence
is not acceptance.

Do not hard-code an upstream end-of-life date here. The runtime owner records the
current CPython 3.13 and Chaquopy support status in each release review. Before
either selected line becomes unsupported, upgrade it or make the provider
unavailable by default. An unsupported interpreter is not eligible for a stable
release merely because an older APK still starts.

## Upgrade and lock regeneration

Treat a Chaquopy, CPython, ABI, AGP, repository, or packaging-policy change as a
coherent runtime upgrade:

1. Update the runtime-selection ADR with the reason, compatibility scope and
   rollback candidate.
2. Pin the intended versions and ABI/package policy before resolving artifacts.
3. Use only the documented, narrowly scoped metadata-bootstrap workflow to
   regenerate dependency locking and verification metadata. Gradle work remains
   serialized with other Codex Gradle clients.
4. Independently review the complete candidate inventory, coordinates, byte
   sizes and SHA-256 values before promoting `locks/python-runtime.lock`.
5. Rebuild from the resolved lock, inspect packaged Python/ABI/native contents,
   run focused JVM and exact-device execution checks, and scale the matrix only
   where the change risk requires it.
6. Update `THIRD_PARTY_NOTICES.md` and its packaged asset copy, then record the
   exact source revision, artifacts, signer and evidence level.

Never combine an old runtime lock with new verification metadata, or a refreshed
host API AAR with an APK whose recorded hash predates that AAR. A source or lock
change invalidates downstream binary/device evidence instead of relabeling it.

## Rollback

The first response to suspected runtime compromise is to disable distribution or
leave the host's explicit Python channel off. A rollback restores one previously
audited, still-supported set of source, host API AARs, runtime inventory and
verification metadata, then produces a newly versioned and signed APK with new
evidence. Do not mix individual files from different baselines.

Rollback must not load Python, plugin native libraries, or user-generated DEX
into the host process; it must not enable online `pip`, silently replay a
dispatched request, or fall through to the JavaScript engine. If no supported
baseline is safe, the provider remains unavailable.

## Trusted-local-script boundary

Python input is user-selected local code and must be treated as trusted for the
permissions and APIs reachable by the plugin UID. The separate APK UID/process,
zero-permission source manifest, bounded Binder/PFD contract and frozen host
capability snapshot reduce host exposure, but Chaquopy exposes a Java bridge.
They do **not** make hostile Python a security sandbox.

Do not add network-fetched code, runtime package installation, arbitrary host
objects, Binder handles, Android `Context`, shell, accessibility or live UI
capabilities without a new threat-model decision. Any such expansion requires
an explicit protocol capability, default-off admission, notice/lock review and
fresh security evidence.
