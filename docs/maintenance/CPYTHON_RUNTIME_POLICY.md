# CPython Runtime Maintenance Policy

Status: R6 release-baseline policy for Plugin 0.1.0 preparation. It defines
ownership and the minimum maintenance path; it is not a release receipt, a
claim that `v0.1.0` has been tagged or published, or a claim that Python code is
sandboxed.

## Ownership

The maintained 0.1.x line assigns all three required roles to
**SuperMonster003**:

- **Runtime owner — SuperMonster003**: tracks the selected Chaquopy and CPython
  lines, evaluates upgrades and end-of-life, and owns runtime regressions.
- **Security owner — SuperMonster003**: triages relevant CVEs and advisories,
  records exposure and mitigations, and can keep the runtime channel disabled.
- **Release owner — SuperMonster003**: rebuilds and reviews locks, verifies
  notices and source availability, and records the exact APK, signer, version,
  Host pair and evidence.

A later delegation must be recorded in the release record. An unassigned role
blocks a stable release.

## Supported baseline, Host pair and source of truth

The runtime baseline is Chaquopy 17.0.0 with CPython 3.13.9, standard library
only, for `arm64-v8a` and `x86_64`. `locks/python-runtime.lock` is the canonical
runtime artifact inventory; `gradle/verification-metadata.xml` supplies
dependency checksums, and `docs/adr/0001-python-runtime-selection.md` records
the selection decision. Prose version strings are descriptive and must not
override those files.

Plugin 0.1.0 is intended to pair with AutoJs6 Host 6.8.0. The final Host
version name/code, source commit, release-AAR distribution manifest and protocol
compatibility bounds have not yet been frozen as one release identity. That is
a release blocker: release notes must state the exact validated Host identity
rather than broaden it to an untested 6.8.0 family.

The official source repository is:

https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime

Repository authorization and release preparation do not prove that a remote,
tag or published release exists. Those facts require independently recorded
publication evidence.

## Long-term release signer

SM003 is the long-term Plugin 0.1.x release signer. Its exact keystore and
certificate SHA-256 identities are machine-pinned in
`locks/release-identity.lock`; that lock, not an alias written in prose, is the
trust source. Private keys, passwords and signing environment details must never
be committed or copied into release evidence.

A signer rotation is an explicit trust migration, not ordinary key renewal. It
requires a recorded security decision, Host pin/admission update, new artifacts
and focused identity/device evidence, user-facing release notes, and a rollback
plan. Never silently accept both the old and new signer, and never relabel
evidence produced under one signer as evidence for the other.

## Security, CVE and end-of-life handling

The security owner reviews CPython security announcements, Chaquopy release
notes/advisories and repository dependency alerts before each stable release
and periodically while that release line is supported. Each relevant report is
classified as affected, not affected or still investigating, with the runtime
version and rationale recorded.

An actively exploited issue, or a critical issue crossing the Python/Java
bridge or plugin UID boundary, keeps distribution disabled until it is patched
or explicitly mitigated. Lower-severity issues receive a recorded disposition
and maintenance target; silence is not acceptance.

Do not hard-code an upstream end-of-life date here. The runtime owner records
the current CPython 3.13 and Chaquopy support status in each release review.
Before either line becomes unsupported, upgrade it or make the provider
unavailable by default.

## Upgrade and lock regeneration

Treat a Chaquopy, CPython, ABI, AGP, repository, Host API AAR, protocol or
packaging-policy change as a coherent runtime upgrade:

1. Update the runtime-selection ADR with the reason, compatibility scope and
   rollback candidate.
2. Pin intended versions, signer and ABI/package policy before resolving
   artifacts.
3. Use only the documented, narrowly scoped metadata-bootstrap workflow to
   regenerate dependency locking and verification metadata. Gradle work remains
   serialized with other Codex Gradle clients.
4. Independently review the complete inventory, coordinates, byte sizes and
   SHA-256 values before promoting a lock.
5. Rebuild from the resolved locks, inspect packaged Python/ABI/native contents,
   run focused JVM and exact-device execution checks, and expand the matrix only
   where the change risk requires it.
6. Update both copies of `THIRD_PARTY_NOTICES.md`, then record the exact source
   revision, artifacts, signer, Host pair and evidence level.

Never combine an old runtime lock with new verification metadata, or a refreshed
Host API AAR with an APK whose recorded hash predates that AAR. A source, lock,
AAR, signer or version change invalidates downstream binary/device evidence
instead of permitting it to be relabeled.

## Hot-plug, failure and rollback behavior

Host restart is not required when the provider changes. Installation or
re-enablement makes the next new execution eligible. A missing or disabled
provider must prompt for installation or enablement and fail closed without
falling through to JavaScript or another engine.

Uninstall, disable or update can kill the Binder for an in-flight execution.
That execution terminates and is never replayed. A later new execution performs
provider discovery again and pins the newly observed component, package,
signing and runtime identity.

The first response to suspected runtime compromise is to disable distribution
or leave the Host's explicit Python channel off. A rollback restores one
previously audited, still-supported set of source, Host API AARs, runtime
inventory and verification metadata, then produces a newly versioned and signed
APK with fresh evidence. Do not mix files from different baselines.

Rollback must not load Python, plugin native libraries or user-generated DEX
into the Host process; enable online `pip`; silently replay a dispatched
request; or fall through to the JavaScript engine. If no supported baseline is
safe, the provider remains unavailable.

## Trusted-local-script boundary

Python input is user-selected local code and must be treated as trusted for the
permissions and APIs reachable by the plugin UID. The separate APK UID/process,
zero-permission source manifest, bounded Binder/PFD contract and frozen Host
capability snapshot reduce Host exposure, but Chaquopy exposes a Java bridge.
They do **not** make hostile Python a security sandbox.

Do not add network-fetched code, runtime package installation, arbitrary Host
objects, Binder handles, Android `Context`, shell, accessibility or live UI
capabilities without a new threat-model decision. Any expansion requires an
explicit protocol capability, default-off admission, notice/lock review and
fresh security evidence.
