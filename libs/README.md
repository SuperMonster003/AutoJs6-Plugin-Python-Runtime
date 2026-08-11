# Host protocol AAR staging

This directory contains the exact, hash-locked Host release API distribution
consumed by the plugin.

Before any Gradle configuration, stage audited **release** artifacts named exactly:

- `common-plugin-api.aar`
- `protocol-wire-api.aar`
- `python-runtime-api.aar`

Record the lowercase SHA-256 of every staged artifact in
`../locks/host-api-aars.lock`. `app/build.gradle.kts` rejects missing files,
debug artifacts, placeholder hashes, extra lock entries, and digest mismatches
during configuration.

Do not commit locally assembled debug AARs or rename debug outputs to bypass this
policy. A stable release must consume the versioned Host 6.8.0 distribution
manifest and the exact three release AARs produced by that clean Host source.
