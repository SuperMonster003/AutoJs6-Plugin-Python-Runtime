# M6 lightweight release process

Status: accepted for the cumulative `0.5.0` release train. This process replaces
the new Roadmap's remaining release ambiguity; it does not replace the frozen
historical verification of the already-published `v0.1.0` tag.

## One cumulative release train

Versions `0.2.x`, `0.3.x`, and `0.4.x` were useful implementation waypoints but
were never published. Their completed capabilities are accumulated into
`0.5.0`; the project will not create retroactive tags or pretend those waypoints
were releases.

The forward sequence is deliberately short:

1. `0.5.0-alpha.N`: current-tree development candidates; incomplete release
   work is allowed and no publication is implied.
2. `0.5.0-beta.1`: feature freeze after the full local gate and the exact
   candidate's manual Android smoke checklist pass.
3. `0.5.0`: first cumulative stable release after `0.1.0`; requires an explicit
   publication instruction, the pinned production signer and Host provenance,
   and the same smoke checklist on the signed candidate.

`1.0.0` remains the later API-stability milestone. It is not a synonym for
"everything in the Roadmap is implemented" and is not pulled forward by M6.

## Version and generated-document rules

- `VERSION_NAME` is SemVer and matches `.readme/common.json.release_target`.
- `VERSION_BUILD` equals the clean repository's Git commit count. The candidate
  commit therefore carries the build number it will have after that commit.
- `v<VERSION_NAME>` is the first entry in every one of the ten locale changelog
  sources, with identical version ordering.
- README and Android changelog outputs exactly match `.python/generate_markdown.py`.
- The three Host API AAR files exactly match `locks/host-api-aars.lock` SHA-256
  values. Refreshing that lock remains a separate dual-repository operation.
- `release/` and `releases/` contain no stale APK before a candidate check.

## Local candidate gate

The quick source profile is read-only and requires a clean committed tree:

```powershell
python -B tools/verify-m6-candidate.py --source-only
```

The full profile first applies the same source checks, then runs all portable
tests, the R2 filesystem-static gate, and the offline debug JVM/APK build:

```powershell
python -B tools/verify-m6-candidate.py --full
```

The full profile requires Python 3.13 and prepends that interpreter to the build
PATH so Chaquopy uses the intended build Python. It searches the current
interpreter, `AUTOJS6_PYTHON313`, `python3.13`, Windows `py -3.13`, and standard
local installation directories in that order. Set `AUTOJS6_PYTHON313` to an
executable or installation directory if automatic discovery is ambiguous.
Gradle is always passed `--offline`; the output is a debug build used only to
prove compilation.

Neither profile invokes ADB, reads `sign.properties`, creates a signed release
APK, writes an evidence receipt, changes Git state, creates a tag, pushes, or
publishes. A `PASS` is local-candidate readiness only. It is necessary but not
sufficient for beta or stable publication.

The historical `tools/verify-r6-release-source.ps1` and
`tools/verify-r6-stable-release.ps1` remain frozen to the `v0.1.0` source and
publication identities. They are not current-tree `0.5.0` gates.

## Manual Android smoke checklist (10 items)

Run these on the exact signed candidate intended for beta/stable promotion and
record only the candidate identity, device identity, PASS/FAIL per item, and a
short failure note. No hash-bound evidence bundle is required.

- [ ] Single-file and project runs show ordered live stdout/stderr and finish
  with the expected terminal state.
- [ ] File, package, relative, circular, module-entry, and project-local
  pure-Python imports use the documented execution root and do not leak state.
- [ ] Snapshot stdin, foreground `input()`/`getpass`, and a background input
  attempt produce their documented value, EOF, cancel, or fail-closed result.
- [ ] Explicit structured JSON and one binary output artifact appear in the
  user-visible destination with the expected bytes; a script without an
  explicit result does not fabricate one.
- [ ] Toast/clipboard/app/device/console/notice capabilities complete, with one
  deliberately invalid argument returning its stable error.
- [ ] Host files, dialogs, and allowed non-Python engine launch work inside the
  execution scope; nested Python remains rejected.
- [ ] Automator, selector, screenshot, find-color, template matching, and OCR
  pass on an eligible setup; unavailable services fail closed without changing
  device accessibility or OCR configuration.
- [ ] A long-running project shows its foreground notification, Stop retires it,
  an immediate rerun succeeds, and an unstopped run survives beyond five minutes.
- [ ] Two rapid Python launches execute in Host FIFO order with fresh process
  generations; stopping a queued launch does not stop the active owner.
- [ ] A bounded scheduled task runs, then Plugin disable/re-enable or in-place
  update is rediscovered without restarting Host; no fallback engine is used.

Any failed applicable item blocks promotion, becomes an issue, and gains one
focused regression before the checklist is rerun. Capability-unavailable paths
count as PASS only when the documented stable error is returned without device
configuration mutation.

## Signed candidate and publication boundary

Creating signed release APKs continues to use the Gradle production-signer,
clean-worktree, commit-count, and Host-provenance gates already present in
`app/build.gradle.kts`. M6 does not weaken them. If the accepted Host source has
advanced without an AAR protocol change, regenerate the three release AARs from
that exact clean Host revision and refresh the lock before building a signed
candidate.

Tag creation, push, GitHub Release creation, asset upload, and stable publication
are external mutations. They occur only after an explicit user instruction and
are never implied by either local M6 gate profile.
