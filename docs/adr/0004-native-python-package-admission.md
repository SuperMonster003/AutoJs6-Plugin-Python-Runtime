# ADR 0004: native Python package admission

Status: Accepted — no package admitted, 2026-08-24

## Context

M4 Path C asked whether the Plugin should embed one or more native Python
packages from Chaquopy's Android wheel index. The evaluated candidates were
Pillow, NumPy and OpenCV because they cover common image-processing and numeric
workloads which project-local pure-Python packages cannot provide.

This evaluation applies the current runtime boundary: Chaquopy 17.0.0,
CPython 3.13.9, Android API 24 or later, and both supported 64-bit ABIs
(`arm64-v8a` and `x86_64`). It does not weaken the requirement that every
direct and transitive native library must work on 16 KiB-page Android devices.
Android's official guidance requires every native dependency to have LOAD
segments aligned to at least `2**14`, and requires APK ZIP alignment as a
separate check:

https://developer.android.com/guide/practices/page-sizes

Chaquopy 17 supports Python 3.13 and 16 KiB pages in its runtime, but its own
tracking issue explicitly says the requirement applies to all wheels as well:

https://github.com/chaquo/chaquopy/issues/1171

## Official-index inventory on 2026-08-24

The only CPython 3.13 Android wheels in Chaquopy's official index for the two
supported ABIs were:

- `pillow==11.0.0` build `0`, depending on `chaquopy-freetype>=2.9.1` and
  `chaquopy-libjpeg>=1.5.3`;
- `numpy==1.26.2` build `0`, depending on `chaquopy-openblas>=0.2.20` and
  `chaquopy-libcxx>=11000`; OpenBLAS additionally depends on
  `chaquopy-libgfortran>=4.9`.

The `opencv-python` and `opencv-python-headless` indexes stop at CPython 3.10.
Their most recent listed Android build is `4.5.1.48-2`, so neither supplies a
wheel compatible with the Plugin's `cp313` runtime. A pip probe constrained to
`android_24_arm64_v8a`, Python 3.13 and ABI `cp313` returned `No matching
distribution found` from the official index.

The exact indexes inspected were:

- https://chaquo.com/pypi-13.1/pillow/
- https://chaquo.com/pypi-13.1/numpy/
- https://chaquo.com/pypi-13.1/opencv-python/
- https://chaquo.com/pypi-13.1/opencv-python-headless/
- https://chaquo.com/pypi-13.1/chaquopy-freetype/
- https://chaquo.com/pypi-13.1/chaquopy-libjpeg/
- https://chaquo.com/pypi-13.1/chaquopy-openblas/
- https://chaquo.com/pypi-13.1/chaquopy-libgfortran/
- https://chaquo.com/pypi-13.1/chaquopy-libcxx/

These Android builds are materially behind the upstream releases which PyPI
reported on the same date: Pillow 12.3.0, NumPy 2.5.2 and opencv-python
5.0.0.93. Version age is not the primary rejection reason, but it increases the
maintenance cost of admitting the old Android builds.

## Reproducible evaluation inputs

The build ran in a detached worktree at source commit
`2ca45ea58b015c5e5df447ff77c6bae37bca571e`, version `0.4.0-alpha.8`.
The only baseline build change was an explicit `buildPython` pointing at the
official CPython 3.13.9 Windows AMD64 full ZIP. Chaquopy requires build Python
to have the same major and minor version as the target runtime. That temporary
tool archive was 33,724,497 bytes with SHA-256
`b87eb2b5d7a31220b56f3ab19b1817065af3dd57997aff752132bc13e7832915`:

https://www.python.org/ftp/python/3.13.9/python-3.13.9-amd64.zip

Candidate builds used Gradle `--offline` and pip `--no-index --find-links`
against a temporary, bounded wheel directory. Pip selected only the following
reviewed official-index files. These files were evaluation inputs only and are
not checked into or distributed by this repository.

| Distribution | ABI | Wheel bytes | SHA-256 |
| --- | --- | ---: | --- |
| Pillow 11.0.0-0 | arm64-v8a | 582,449 | `0d380685ae11d55ab6ac8152b1eb79999913c458f412fa50d7cc9157558bd174` |
| Pillow 11.0.0-0 | x86_64 | 603,290 | `5a9a22a405d55126efa6dad46d700e118ec2ff177d9a793050336d54fc0ed55b` |
| chaquopy-freetype 2.9.1-2 | arm64-v8a | 533,849 | `7a8262dc69d1bbf7209b3b7576744743670bd5a8cba48c7d8f08c151943ccbc7` |
| chaquopy-freetype 2.9.1-2 | x86_64 | 567,803 | `831e0fd721d132b7b04946399d714de9945acc56dffa34f3c037592cb17c8de1` |
| chaquopy-libjpeg 1.5.3-1 | arm64-v8a | 176,242 | `5555be57a2633fb5a3c0c810e89c8b705c471e3dabd95aa596fc7fdd48322728` |
| chaquopy-libjpeg 1.5.3-1 | x86_64 | 147,477 | `0ae61fe258eb17a34e66fb6b1c233eb6c5e6a8854e0900a1806422e9f5625a86` |
| NumPy 1.26.2-0 | arm64-v8a | 5,085,708 | `05db9adc14aa49f075a5ea5c59559c361e54efd926f321eddd3b37e2fd05b721` |
| NumPy 1.26.2-0 | x86_64 | 6,412,051 | `5b24863b756d2a0adc0405a7c1a74f9acfd7c3aa66b920c8760daafc12a26da7` |
| chaquopy-openblas 0.2.20-5 | arm64-v8a | 4,342,777 | `1e8e67a4f9e2fcde384890678bafbf7ffefe7b2cb4887e5c2996ba7607f4324c` |
| chaquopy-openblas 0.2.20-5 | x86_64 | 5,325,629 | `6b258351c0ce1229f71057808f51117ab96c291d3ef1887a92e1d5fb75d319be` |
| chaquopy-libgfortran 4.9-0 | arm64-v8a | 495,679 | `0b4caed1147f2a19707d4ba730afea57f7b8f2d8c046d8a48cf49377741c4604` |
| chaquopy-libgfortran 4.9-0 | x86_64 | 541,094 | `375b3f8949f1826a969586fa529178f469f5e86565896be201264cf7faa35ee8` |
| chaquopy-libcxx 180000-0 | arm64-v8a | 413,239 | `811547210b01eefb0fb850fd35bd27b53a00a76b9466b8c03e049b7e8175004b` |
| chaquopy-libcxx 180000-0 | x86_64 | 422,724 | `dd56e48a66d08e352a1aacb6e3e9ff50788ae1b140b30bbd33d8bbb6854390c4` |

License files were present in every evaluated closure. The inventory included
MIT-CMU/HPND for Pillow, the FreeType Project License, the IJG/BSD/zlib
libjpeg-turbo terms, NumPy's BSD-3-Clause and bundled notices, BSD-3-Clause for
OpenBLAS, GPLv3-or-later with the GCC Runtime Library Exception for
libgfortran, and Apache-2.0 with LLVM Exceptions for libc++. No incompatibility
was identified during this evaluation, but admission would still require the
complete texts in both release-notice surfaces.

## Build and size evidence

All measurements below are temporary debug candidates, not release artifacts
or publication evidence. The baseline and each candidate used the same explicit
CPython 3.13 build Python, so byte deltas do not include a build-Python policy
change.

| APK output | Baseline bytes | Pillow bytes | Pillow delta | NumPy bytes | NumPy delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| `arm64-v8a` | 23,748,044 | 25,802,527 | +2,054,483 | 45,679,208 | +21,931,164 |
| `x86_64` | 23,764,404 | 25,818,887 | +2,054,483 | 45,695,568 | +21,931,164 |
| universal | 34,660,395 | 36,714,878 | +2,054,483 | 56,591,559 | +21,931,164 |

Both candidates completed `:app:assembleDebug --offline`. All three Pillow APKs
and all three NumPy APKs passed `zipalign -c -P 16 4`. Those successful APK ZIP
checks do not repair an incompatible ELF LOAD segment inside the archive.

## Native-library audit

Every direct and transitive file matching `.so` or `.so.*` was extracted from
both ABI closures and inspected with NDK 29 `llvm-readelf -lW`. The minimum LOAD
alignment was:

| Distribution | Native files per ABI | arm64-v8a minimum | x86_64 minimum | 16 KiB result |
| --- | ---: | ---: | ---: | --- |
| Pillow 11.0.0-0 | 5 | `0x4000` | `0x4000` | pass |
| chaquopy-freetype 2.9.1-2 | 1 | `0x1000` | `0x1000` | **fail both ABIs** |
| chaquopy-libjpeg 1.5.3-1 | 1 | `0x10000` | `0x1000` | **fail x86_64** |
| NumPy 1.26.2-0 | 19 | `0x4000` | `0x4000` | pass |
| chaquopy-openblas 0.2.20-5 | 1 | `0x10000` | `0x1000` | **fail x86_64** |
| chaquopy-libgfortran 4.9-0 | 1 | `0x10000` | `0x1000` | **fail x86_64** |
| chaquopy-libcxx 180000-0 | 1 | `0x4000` | `0x4000` | pass |

Pillow therefore fails through FreeType even on arm64-v8a. NumPy's arm64-v8a
closure passes the static alignment test, but the supported x86_64 closure does
not. Shipping only one supported ABI would be a separate product and release
policy change, not a package workaround.

The 4 KiB files cannot be made compliant by editing only the ELF `p_align`
field. Their later LOAD segments have a virtual-address/offset difference of
`0x1000`, which is not congruent at `0x4000`; they must be relinked with a
16 KiB-compatible layout.

## Targeted-remediation assessment

Chaquopy publishes the relevant source recipes, but its current guidance says
Python 3.13-or-later Android wheels should be built with cibuildwheel on Linux
or macOS:

https://github.com/chaquo/chaquopy/blob/master/server/pypi/README.md

This Windows evaluation host has neither a Docker engine nor an installed WSL
distribution. Installing a new cross-build environment, silently repacking old
binaries, or publishing locally relinked wheels without a reviewable build
recipe would not be a targeted low-risk fix. A valid repair requires a pinned
Linux/macOS CI or equivalent builder, NDK r28 or later (or explicit 16 KiB
linker flags), source and patch locks, dual-ABI wheel hashes, licenses, and the
same clean offline application build and device tests as an official wheel.

OpenCV additionally requires a new CPython 3.13 Android build and its much
larger source/dependency/license closure. It cannot be repaired by selecting an
existing official-index artifact.

## Decision

Decision code: `NOT_ADMITTED`.

Candidate dispositions are:

- Pillow: `BUILDABLE_NOT_ADMITTED_16K`;
- NumPy: `BUILDABLE_NOT_ADMITTED_16K_AND_SIZE`;
- OpenCV: `NOT_BUILDABLE_NO_CP313_WHEEL`.

Close the M4 Path C evaluation without embedding a native package. Keep
`app/build.gradle.kts` free of a Chaquopy `pip` block and keep
`locks/python-runtime.lock` at package policy `stdlib-only`, package count zero
and online pip disabled. Do not add candidate wheels or candidate license texts
as though they were release dependencies. Missing imports keep their ordinary
`ModuleNotFoundError` behavior, and Path A remains limited to pure-Python
project-local dependencies.

No release build, signing operation or device installation was justified after
the static dual-ABI compatibility gate failed. This decision makes no new
device claim.

## Admission gate for a future native proposal

A later proposal may replace `NOT_ADMITTED` only when all of the following are
reviewable together:

1. Name a recurring user case and the smallest direct and transitive native
   distribution closure which solves it.
2. Provide immutable dual-ABI wheels, exact versions and SHA-256 hashes from an
   official source or a repository-owned reproducible build recipe.
3. Pin a same-major/minor CPython build tool and make a clean build independent
   of an unrecorded developer-machine Python installation.
4. Configure pip with `--no-index`, bounded `--find-links` and
   `--require-hashes`; prove a clean build with network access denied.
5. Inventory every `.so` and `.so.*` in the complete closure. Every LOAD
   segment for both `arm64-v8a` and `x86_64` must have alignment at least
   `0x4000`, and every output APK must pass `zipalign -c -P 16 4`.
6. Check in and package all required license and incorporated-software notices,
   including transitive native runtimes, from the same locked inventory.
7. Record exact baseline and candidate deltas for arm64-v8a, x86_64 and
   universal release APKs, with an accepted size budget before admission.
8. Exercise import, exact metadata version and a useful public-engine operation
   on both supported ABIs, including a 16 KiB-page environment.
9. Review candidate freshness and known security exposure; do not freeze a
   materially stale wheel merely because it imports once.

The default remains rejection when any item is absent. A runtime installer in
M4 Path D cannot bypass this native admission gate.
