# M6 Android smoke results

Status: the exact SM003-signed `0.5.0-alpha.6` and `0.5.0-beta.1` candidates
each passed all ten manual Android smoke items. The beta result admits the
cumulative release train to `0.5.0` stable-candidate preparation. This is a
concise operator record, not a hash-bound evidence bundle and not a publication
receipt.

## OnePlus OPD2413 functional and OEM activation run

On 2026-08-25, OnePlus OPD2413 (Android 15 / API 35 / arm64-v8a) ran the full
ten-item checklist on a matching Android-Debug Host/Plugin pair built from the
alpha.6 source. All ten items passed, including the optional foreground input
cancel path and the independent PowerShell ADB verification of the fixed
34-byte output artifact.

The same device first reproduced the OEM package-manager state behind the
reported InfoService failure: a fresh Plugin remained
`stopped=true/notLaunched=true`, so the first explicit bind returned false.
Plugin Center `ACTIVATE` invoked the new signature-protected NoDisplay
`WakeActivity`, cleared that state and automatically enabled the Plugin. The
startup probe then completed successfully. This run validated functionality
and OEM recovery, but its Android-Debug signer did not qualify the production
candidate.

Installed identities read back for that run were:

| Package | Version | APK SHA-256 | Signer SHA-256 |
| --- | --- | --- | --- |
| AutoJs6 | 6.8.0 / 5276 | `AC99BB6E82651850B3415813993A6C3CADFC9FF6BECEF603EFB210B246A2C79B` | `2E64822E13A6C80C12E1C4B47E8FB32D1E9334526289DA75777B7A79145DE4B8` |
| Python Runtime | 0.5.0-alpha.6 / 89 | `F59785824AF7171C9F8508F4513BD90CEC78C35928ECBC59B9A439C976BDCA93` | `2E64822E13A6C80C12E1C4B47E8FB32D1E9334526289DA75777B7A79145DE4B8` |

## QV710AF65F exact SM003 alpha.6 candidate run

On 2026-08-25, Sony XQ-AT72 (`QV710AF65F`, Android 12 / API 31 /
arm64-v8a) ran all ten items after an in-place update to the formal alpha.6
arm64 APK. The operator reported every item PASS.

The formal Plugin was installed with `adb install --no-streaming -r -t`, with
no uninstall and no application-data clearing. Pulling the installed
`base.apk` back from the device produced the exact formal artifact SHA-256.
Host and Plugin both used the production SM003 signer:

| Package | Version | APK SHA-256 | Signer SHA-256 |
| --- | --- | --- | --- |
| AutoJs6 | 6.8.0 / 5276 | `20FFE49EA9D9F1D637F96BAB1A8E251F343643F26963131F5CDC6114E96D43C8` | `31A681FCFFFB3E428420CAE280DED89292B12A3B0F59E19B7A73E32A8AE4C213` |
| Python Runtime | 0.5.0-alpha.6 / 89 | `CA6252ACE475FFA554FE414DEB09386F0F5BED79F2CC135847FEF9A3424FD8ED` | `31A681FCFFFB3E428420CAE280DED89292B12A3B0F59E19B7A73E32A8AE4C213` |

The Plugin APK was v2-signed, `debuggable=false`, `testOnly=false`, and
byte-identical to
`autojs6-plugin-python-runtime-v0.5.0-alpha.6-arm64-v8a-dd5ab638.apk` from
source commit `9ac32da5fd33eafdfe684e12e51f1dc79101b8e1`.

Items 2, 3 and 4 used the deterministic projects in
[`examples/python/m6_manual_smoke`](../../examples/python/m6_manual_smoke).
That included file/module import roots, two-run state cleanup, finite stdin,
foreground visible/hidden input, scheduled-background EOF, cancel mapping,
explicit JSON, one fixed binary artifact and JSON-looking stdout without
result fabrication. The artifact verifier independently pulled the published
file and confirmed 34 bytes with SHA-256
`2B4A5E4BB7EB7C83D6241C5176D01EEDD31873FA63B28DE10F5553D8FBD25BD4`.

## QV710AF65F exact SM003 beta.1 candidate run

On 2026-08-25, the same Sony XQ-AT72 (`QV710AF65F`, Android 12 / API 31 /
arm64-v8a) received the formal beta.1 arm64 APK as an in-place update. The
operator reran all ten projects and reported every item PASS.

After the report, a read-only ADB audit confirmed that user 0 had the Plugin
active as `0.5.0-beta.1`/versionCode 91 with
`stopped=false`/`notLaunched=false`. The installed Host identity was unchanged.
Both installed APKs were pulled without changing device state and independently
verified with Android build-tools 37:

| Package | Version | APK SHA-256 | Signer SHA-256 |
| --- | --- | --- | --- |
| AutoJs6 | 6.8.0 / 5276 | `20FFE49EA9D9F1D637F96BAB1A8E251F343643F26963131F5CDC6114E96D43C8` | `31A681FCFFFB3E428420CAE280DED89292B12A3B0F59E19B7A73E32A8AE4C213` |
| Python Runtime | 0.5.0-beta.1 / 91 | `80FA480ACAE1C66C07DC59C9B588603B7F787E21DE72BB5A5521A2732B0C695F` | `31A681FCFFFB3E428420CAE280DED89292B12A3B0F59E19B7A73E32A8AE4C213` |

The pulled Plugin was byte-identical to
`autojs6-plugin-python-runtime-v0.5.0-beta.1-arm64-v8a-adc0d68b.apk` from
source commit `4bbae75dbfb496995e5278684024f63ae9f71a43`. It remained v2-signed,
`debuggable=false`, `testOnly=false`, and carried the production SM003
certificate shared with Host.

## Claim boundary

The first QV710AF65F run closed the production-signed alpha-to-beta gate; the
second exact beta.1 run closes the beta-to-stable-source gate. It authorizes
preparing a `0.5.0` candidate under
[`M6_RELEASE_PROCESS.md`](M6_RELEASE_PROCESS.md). It does not qualify the new
stable APK before that exact APK is built and tested, and it does not create or
publish a tag, GitHub Release, stable publication, or post-publication receipt.
Publication still requires the full local gate, exact signed stable artifact
checks, the same manual checklist on that installed stable candidate, and an
explicit publication instruction.
