# Host protocol AAR staging

This directory intentionally contains no binary AARs in the R2 scaffold.

Before any Gradle configuration, stage audited **release** artifacts named exactly:

- `protocol-wire-api.aar`
- `python-runtime-api.aar`

Then replace the `REQUIRED_SHA256` values in `../locks/host-api-aars.lock` with the lowercase SHA-256 of each staged artifact. `app/build.gradle.kts` rejects missing files, debug artifacts, placeholder hashes, and digest mismatches during configuration.

Do not commit locally assembled debug AARs or rename debug outputs to bypass this policy. The eventual release workflow must consume a host-published, versioned protocol distribution.
