# Python Runtime Plugin Roadmap

Status: R6 stable-release track for Plugin 0.1.0. The official public repository,
`master` branch and exact stable source identity exist. Tag, GitHub Release and
asset publication facts are established only by an independent production
receipt, not by mutable status prose or checklist state in the tagged source.

This roadmap favors exact, reviewable release progress. Source/static, Android
build, APK packaging, Binder/device and public-release evidence remain distinct.
A completed lower evidence level never substitutes for a later one.

## Accepted release baseline

- [x] Keep Python in an independently installed APK/process. The normal Host
  always contains only the adapter; execution still selects the one fixed
  official component, requires an installed and enabled eligible plugin, and
  never falls back to a legacy engine. Packaged INRT apps remain unsupported.
- [x] Use Chaquopy 17.0.0 / CPython 3.13.9, standard library only, for
  `arm64-v8a` and `x86_64`.
- [x] Treat user-selected local Python as trusted for the plugin UID; do not
  claim a hostile-code sandbox.
- [x] Assign runtime, security and release ownership to SuperMonster003.
- [x] Select the SM003 identity pinned by `locks/release-identity.lock` as the
  long-term release signer.
- [x] Target Plugin 0.1.0 for pairing with AutoJs6 Host 6.8.0.
- [x] Freeze and enforce AutoJs6 Host versionCode `5275` as the minimum
  compatibility boundary for Plugin 0.1.0.
- [x] Freeze hot-plug semantics: no Host restart; installation/re-enablement
  affects the next new execution; missing/disabled prompts and fails closed;
  in-flight Binder death terminates without replay; later executions rediscover
  and pin provider identity.

## R6-P1: implemented and locally evidenced baseline

- [x] Implement the explicit Binder/PFD execution provider in
  `:python_runtime`, with exact-host/signer admission, bounded transport, one
  active session and process-restart-only cancellation.
- [x] Pin Gradle, Host API AAR, Chaquopy/CPython and dependency inventories with
  fail-closed source/build gates.
- [x] Build and inspect arm64-v8a, x86_64 and universal APK variants for the
  declared permission, ABI, native, license and signing policy.
- [x] Exercise focused finite execution, structured failure, output limits,
  cancellation, timeout, Binder death/rebind, reliable-pipe failure and identity
  boundaries on an API 31 arm64 device.
- [x] Preserve those runs as local RC/partial evidence only. They are not a
  public stable-release receipt and x86_64 remains packaging-only evidence.

## R6-P2: final source and Host-pair freeze

- [x] Accept the runtime selection, trusted-local boundary, long-term signer,
  ownership and hot-plug maintenance policy.
- [x] Freeze the AutoJs6 Host version name/code and enforceable compatibility
  floor as `6.8.0` / `5275`.
- [x] Freeze clean Host source
  `2caddcb763b39f0bf450909742fa6ec4caba27a8` and three-AAR manifest SHA-256
  `9f296ad45c24b7eb3e217e4d0ce6c96ba2593966b2bed1db1f2846d658987818`.
- [x] Add an explicit foreground install/enable prompt for Explorer, Editor,
  Python Project and Floating Menu launches. Background tasks, broadcasts,
  services and direct engine calls retain stable errors and never open UI.
- [x] Compile the Host adapter and Plugin INFO service against the exact local
  three-AAR distribution (`common-plugin-api`, `protocol-wire-api`, and
  `python-runtime-api`) while keeping dirty-tree evidence non-publishable.
- [x] Declare the exact Official Index source identity in `defaultConfig` as
  `plugin_id=python-runtime`, `plugin_engine=python`, and
  `plugin_variant=cpython-3.13`; keep INFO metadata on those same BuildConfig
  values without extending the Index schema.
- [x] Regenerate the Host release-AAR distribution after the final Host commit
  and stage the Plugin AAR lock for that exact manifest.
- [x] Set the stable version to `0.1.0`, enforce `minHostVersionCode=5275`, and
  set `VERSION_BUILD=11` for this single final source-freeze commit.
- [x] Freeze the final Host AAR lock and Plugin identity in this one commit; once
  committed, its repository commit count is exactly `11`, equal to
  `VERSION_BUILD` without requiring a follow-up identity edit.

Exit criterion: one clean Host identity and one clean Plugin source identity,
with all locks/notices/version metadata referring to those exact sources.

## R6-P3: focused exact-artifact acceptance

- [ ] Run the release source/supply gate and assemble the stable APKs from the
  frozen commit; record exact APK, lock, signer and Host AAR identities.
- [ ] Re-run the smallest concentrated Binder/device suite covering positive
  execution, missing/disabled/re-enable/uninstall/reinstall/update behavior,
  in-flight death without replay, later rediscovery, signer/UID admission and
  verified package restoration.
- [ ] Produce an independent pre-publication receipt that references the exact
  source and artifact hashes and truthfully records `published=false`.

Exit criterion: fresh P2/P3 evidence for the exact release artifacts. Existing
RC receipts are historical and may be referenced as superseded, never edited or
promoted.

A complete API 24-36 by ABI matrix and a new multi-hour soak are not automatic
0.1.0 gates. Expand testing only for a concrete compatibility, ABI, lifecycle or
security risk; otherwise disclose the proven API 31 arm64 device cell and
x86_64 packaging-only status.

## R6-P4: official publication and production receipt

- [x] Create the official public repository at
  `https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime`, without an
  unrelated generated initial commit, and push the release-preparation
  `master` branch.
- [ ] Push the final frozen `0.1.0` source commit to `master` and independently
  verify that the remote branch resolves to that exact commit.
- [ ] Create and push lightweight tag `v0.1.0` at the exact release commit, in
  line with the existing AutoJs6 plugin family convention.
- [ ] Create a draft GitHub release and upload only stable distributable APKs
  plus checksums, provenance and applicable license/source materials.
- [ ] Publish the GitHub release, then independently query the public tag,
  release and assets instead of inferring publication from a local command.
- [ ] Generate a production receipt containing the release URL/ID/time, tag
  commit, asset hashes, SM003 signer identity, exact Host pair, P2/P3 evidence
  hashes, owners and disclosed device/ABI limits; upload and download-verify it.
- [ ] Update the Host completion roadmap with the immutable public receipt and
  the artifact-producing source commits. Do not mutate the tagged Plugin source
  merely to record post-publication facts.

Exit criterion: the independently verified production receipt—not a checklist
edit—establishes `published=true` and stable-release completion.

## Maintenance after 0.1.0

- [ ] Triage Chaquopy/CPython advisories and support status under
  `docs/maintenance/CPYTHON_RUNTIME_POLICY.md`.
- [ ] Treat runtime, ABI, Host AAR/protocol, signer or capability changes as new
  source identities requiring risk-proportional fresh evidence.
- [ ] Keep missing, disabled or unsafe providers unavailable rather than
  retrying, replaying or falling back.
