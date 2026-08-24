# ADR 0003: build-time pure-Python package admission

Status: Accepted — no package admitted, 2026-08-24

## Context

M4 Path A already permits a trusted project to carry pure-Python distributions
in its immutable workspace snapshot. That path keeps package selection and size
opt-in for each project, preserves ordinary import and `importlib.metadata`
semantics, and does not add a runtime installer.

M4 Path B asked whether a small high-frequency package set should instead be
embedded in every Plugin APK with Chaquopy's build-time pip integration. The
focused candidate was the same five-distribution closure used by the accepted
Path A example:

- `requests==2.34.2`;
- `urllib3==2.7.0`;
- `certifi==2026.7.22`;
- `charset-normalizer==3.4.9`; and
- `idna==3.18`.

The pinned Chaquopy 17.0.0 Gradle source exposes `pip.install` and arbitrary
`pip.options`, then invokes `chaquopy.pip_install` in a separate build-Python
process. Gradle's `--offline` state is not automatically passed to that pip
subprocess. A bare `install("requests==...")` can therefore resolve from a
package index even when the surrounding Gradle dependency graph is offline.

The repository contains no reviewed build-time wheelhouse, hashed pip lock or
packaged license set for this candidate. The evaluation deliberately did not
download those inputs: doing so would make the result dependent on mutable
network state and would contradict the project's normal offline build claim.

## Evidence and value assessment

The `0.4.0-alpha.7` stdlib-only current-tree candidate produced these locally
built debug APK baselines. They are candidate build measurements, not a
publication or stable-release claim.

| APK output | Baseline bytes |
| --- | ---: |
| `arm64-v8a` | 23,709,688 |
| `x86_64` | 23,726,048 |
| universal | 34,622,039 |

A package delta is intentionally not reported. There is no immutable candidate
input from which another developer can reproduce that delta, so treating a
downloaded local cache as evidence — or reporting a zero-byte delta — would be
misleading. The missing hermetic input is itself an admission blocker before
APK-size comparison begins.

The candidate's principal benefit is shorter setup for scripts which choose
`requests`. Its costs apply to every installation: unconditional APK bytes, a
five-distribution update and vulnerability-management cadence, additional
licenses and notices, and a second dependency lock surface. `charset_normalizer`
alone does not provide a compelling general-purpose API. Standard-library
networking is already available, while users who need this exact stack can use
the accepted Path A workflow. That workflow was exercised with 125 runtime
files, no native library suffixes, and canonical tree SHA-256
`880EBB02E4C264F9D8B82521C090F7592ABF0663E67BFC6DC4F224CB636F101B`.

## Decision

Decision code: `NOT_ADMITTED`.

Keep the embedded runtime stdlib-only. Do not add a Chaquopy `pip` block, do not
package `requests`, `charset_normalizer` or their transitive dependencies, and
do not add candidate licenses as though those packages were distributed.
`locks/python-runtime.lock` therefore remains:

```properties
python.packages.policy=stdlib-only
python.packages.count=0
online.pip.allowed=false
```

This closes the M4 Path B evaluation; it does not claim that Chaquopy is unable
to package the candidate. It records that the current benefit does not justify
changing the default APK and that the available inputs do not meet the
repository's reproducibility boundary.

Missing third-party imports continue to raise ordinary `ModuleNotFoundError`.
Neither this decision nor Path A enables automatic resolution, online pip or a
runtime installer.

## Admission gate for a future proposal

A later proposal may replace `NOT_ADMITTED` only when all of the following are
part of one reviewable change:

1. Record a concrete, recurring user case which is materially worse through
   Path A and name the smallest distribution closure which solves it.
2. Provide repository-owned or equivalently immutable offline wheel inputs and
   a requirements file with exact versions and SHA-256 hashes. No package index
   may be needed after a clean checkout.
3. Configure pip with `--no-index`, a bounded local `--find-links` source and
   `--require-hashes`; run the build once with network access denied and after
   deleting prior Chaquopy pip task outputs.
4. Extend the exact-key runtime lock with package name, normalized version,
   wheel filename, SHA-256, source and license identity for every distribution.
5. Check in and package each required upstream license text, then update both
   root and in-app third-party notices from the same reviewed inventory.
6. For this pure-Python path, admit only compatible `py3-none-any` wheels and
   fail the inventory scan on `.so`, `.pyd`, `.dll`, `.dylib` or executable
   payloads. Native distributions belong to the separate M4 Path C decision.
7. Build `arm64-v8a`, `x86_64` and universal release outputs from identical
   clean inputs, report each exact baseline and candidate byte delta, and state
   the accepted size budget before changing the package policy.
8. Exercise imports, exact `importlib.metadata` versions and the intended public
   engine use case on both supported ABIs. Repeat the offline build from empty
   pip task outputs to prove that no resolution escaped the lock.

The default remains rejection when any item is absent. M4 Path D runtime
installation is a separate product and security decision and cannot be enabled
as a shortcut around this gate.
