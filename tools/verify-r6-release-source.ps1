[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$blockers = [System.Collections.Generic.List[string]]::new()

function Add-Blocker([string] $Message) {
    $blockers.Add($Message)
}

function Read-UniqueProperties([string] $Path) {
    $properties = @{}
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $properties
    }
    $lineNumber = 0
    foreach ($rawLine in Get-Content -LiteralPath $Path -Encoding UTF8) {
        $lineNumber++
        $line = $rawLine.Trim()
        if ($line.Length -eq 0 -or $line.StartsWith('#') -or $line.StartsWith('!')) {
            continue
        }
        $separator = $line.IndexOf('=')
        if ($separator -le 0) {
            Add-Blocker "Malformed property at $([IO.Path]::GetFileName($Path)):$lineNumber"
            continue
        }
        $key = $line.Substring(0, $separator).Trim()
        $value = $line.Substring($separator + 1).Trim()
        if ($properties.ContainsKey($key)) {
            Add-Blocker "Duplicate property $key in $([IO.Path]::GetFileName($Path))"
            continue
        }
        $properties[$key] = $value
    }
    return $properties
}

function Get-Sha256([string] $Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Invoke-GitReadOnly([string[]] $Arguments) {
    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $output = & git -C $repoRoot @Arguments 2>$null
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
    if ($exitCode -ne 0) {
        return $null
    }
    return (($output | Out-String).Trim())
}

$appBuildPath = Join-Path $repoRoot 'app/build.gradle.kts'
$appBuild = if (Test-Path -LiteralPath $appBuildPath -PathType Leaf) {
    Get-Content -Raw -LiteralPath $appBuildPath -Encoding UTF8
} else {
    Add-Blocker 'app/build.gradle.kts is missing'
    ''
}

function Read-RequiredSource([string] $RelativePath) {
    $path = Join-Path $repoRoot $RelativePath
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        Add-Blocker "Required release source is missing: $RelativePath"
        return ''
    }
    return Get-Content -Raw -LiteralPath $path -Encoding UTF8
}

$manifest = Read-RequiredSource 'app/src/main/AndroidManifest.xml'
$metadataSource = Read-RequiredSource 'app/src/main/java/io/github/supermonster003/autojs6/plugin/python/runtime/PythonRuntimeMetadata.kt'
$pluginInfoSource = Read-RequiredSource 'app/src/main/java/io/github/supermonster003/autojs6/plugin/python/runtime/PythonRuntimePluginInfoService.kt'
$runtimeAdr = Read-RequiredSource 'docs/adr/0001-python-runtime-selection.md'
$maintenancePolicy = Read-RequiredSource 'docs/maintenance/CPYTHON_RUNTIME_POLICY.md'

foreach ($marker in @(
    'releaseSigningPropertyNames',
    'releaseSigningReady',
    'locks/release-identity.lock',
    'releaseSigningStoreIsPinned',
    'storeFile.sha256() == lockedReleaseKeystoreSha256',
    '0d6b79e4d4efe77829dbcc2e21096931ba7b0349df82f3b58c3e9d24e84f1df0',
    '31a681fcfffb3e428420cae280ded89292b12a3b0f59e19b7a73e32a8ae4c213',
    'unsigned release artifacts are forbidden',
    'VERSION_BUILD must equal the Git commit count',
    'Release artifact creation requires a clean Git worktree',
    'Release artifact creation requires a clean Host HEAD',
    'getOutputFileName',
    '?: "universal"',
    'rootProject.name',
    'collectReleaseFiles',
    'appendDigestToReleasedFiles'
)) {
    if (-not $appBuild.Contains($marker)) {
        Add-Blocker "Release source marker is missing: $marker"
    }
}

if ($appBuild -notmatch 'releaseSigningPropertyNames\s*=\s*setOf\("storeFile",\s*"storePassword",\s*"keyAlias",\s*"keyPassword"\)') {
    Add-Blocker 'Release signing guard does not declare the exact four required property names'
}
if ($appBuild -notmatch '\$\{rootProject\.name\}-v\$normalizedVersion-\$architecture\.apk') {
    Add-Blocker 'Deterministic version and ABI APK naming is missing'
}

$versionProperties = Read-UniqueProperties (Join-Path $repoRoot 'version.properties')
$versionName = $versionProperties['VERSION_NAME']
$versionBuild = 0
if ([string]::IsNullOrWhiteSpace($versionName)) {
    Add-Blocker 'VERSION_NAME is missing'
} elseif ($versionName -cne '0.1.0') {
    Add-Blocker 'VERSION_NAME must be exactly 0.1.0 for the stable source freeze'
}
if (-not [int]::TryParse($versionProperties['VERSION_BUILD'], [ref] $versionBuild) -or $versionBuild -le 0) {
    Add-Blocker 'VERSION_BUILD must be a positive integer'
}

if ($metadataSource -notmatch 'minHostVersionCode\s*=\s*[1-9][0-9]*L') {
    Add-Blocker 'Python runtime metadata does not enforce the final Host 6.8.0 minimum version code'
}
if ($pluginInfoSource -notmatch 'class\s+PythonRuntimePluginInfoService\s*:\s*Service\(\)' -or
    $pluginInfoSource -notmatch 'IPluginInfoProvider\.Stub') {
    Add-Blocker 'Plugin Center INFO service implementation is missing or incomplete'
}
if ($manifest -notmatch 'android:name="\.PythonRuntimePluginInfoService"' -or
    $manifest -notmatch 'android:name="org\.autojs\.plugin\.INFO"') {
    Add-Blocker 'Plugin Center INFO service manifest declaration is missing'
}
if ($runtimeAdr -notmatch 'Status:\s*accepted for 0\.1\.0') {
    Add-Blocker 'Runtime ADR is not accepted for 0.1.0'
}
foreach ($owner in @('Runtime owner', 'Security owner', 'Release owner')) {
    if ($maintenancePolicy -notmatch "(?s)$owner.*SuperMonster003") {
        Add-Blocker "$owner is not assigned to SuperMonster003"
    }
}

$head = Invoke-GitReadOnly @('rev-parse', '--verify', 'HEAD')
if ($null -eq $head -or $head -notmatch '^[0-9a-fA-F]{40,64}$') {
    Add-Blocker 'Git HEAD is absent; the repository is not a traceable release source'
} else {
    $commitCountText = Invoke-GitReadOnly @('rev-list', '--count', 'HEAD')
    $commitCount = 0
    if (-not [int]::TryParse($commitCountText, [ref] $commitCount)) {
        Add-Blocker 'Git commit count is unavailable'
    } elseif ($versionBuild -ne $commitCount) {
        Add-Blocker 'VERSION_BUILD does not equal the Git commit count'
    }
    $status = Invoke-GitReadOnly @('status', '--porcelain', '--untracked-files=all')
    if ($null -eq $status -or $status.Length -ne 0) {
        Add-Blocker 'Git worktree is not clean'
    }
}

$signPath = Join-Path $repoRoot 'sign.properties'
$signProperties = Read-UniqueProperties $signPath
$releaseIdentityPath = Join-Path $repoRoot 'locks/release-identity.lock'
$releaseIdentity = Read-UniqueProperties $releaseIdentityPath
$expectedReleaseIdentity = [ordered]@{
    'format' = '1'
    'host.package' = 'org.autojs.autojs6'
    'plugin.package' = 'io.github.supermonster003.autojs6.plugin.python.runtime'
    'release.keystore.sha256' = '0d6b79e4d4efe77829dbcc2e21096931ba7b0349df82f3b58c3e9d24e84f1df0'
    'release.certificate.sha256' = '31a681fcfffb3e428420cae280ded89292b12a3b0f59e19b7a73e32a8ae4c213'
}
if (-not (Test-Path -LiteralPath $releaseIdentityPath -PathType Leaf)) {
    Add-Blocker 'Release identity lock is missing'
}
if ($releaseIdentity.Count -ne $expectedReleaseIdentity.Count) {
    Add-Blocker 'Release identity lock contains missing or unexpected keys'
}
foreach ($entry in $expectedReleaseIdentity.GetEnumerator()) {
    if ($releaseIdentity[$entry.Key] -cne $entry.Value) {
        Add-Blocker "Release identity lock mismatch for $($entry.Key)"
    }
}
foreach ($key in $releaseIdentity.Keys) {
    if (@($expectedReleaseIdentity.Keys) -cnotcontains [string] $key) {
        Add-Blocker "Release identity lock contains unexpected key: $key"
    }
}
$requiredSigningKeys = @('storeFile', 'storePassword', 'keyAlias', 'keyPassword')
foreach ($key in $requiredSigningKeys) {
    if ([string]::IsNullOrWhiteSpace($signProperties[$key])) {
        Add-Blocker "sign.properties is missing required key: $key"
    }
}
if (-not [string]::IsNullOrWhiteSpace($signProperties['storeFile'])) {
    $storePathValue = $signProperties['storeFile'].Replace('\\:', ':').Replace('\\\\', '\')
    $storePath = if ([IO.Path]::IsPathRooted($storePathValue)) {
        $storePathValue
    } else {
        Join-Path (Join-Path $repoRoot 'app') $storePathValue
    }
    $storeReadable = Test-Path -LiteralPath $storePath -PathType Leaf
    if ($storeReadable) {
        try {
            $stream = [IO.File]::Open($storePath, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::ReadWrite)
            $stream.Dispose()
        } catch {
            $storeReadable = $false
        }
    }
    if (-not $storeReadable) {
        Add-Blocker 'The release keystore declared by sign.properties is not a readable file'
    } elseif ((Get-Sha256 $storePath) -cne $expectedReleaseIdentity['release.keystore.sha256']) {
        Add-Blocker 'The release keystore bytes differ from release-identity.lock'
    }
}

$gitignorePath = Join-Path $repoRoot '.gitignore'
$gitignore = if (Test-Path -LiteralPath $gitignorePath -PathType Leaf) {
    Get-Content -Raw -LiteralPath $gitignorePath -Encoding UTF8
} else {
    ''
}
if ($gitignore -notmatch '(?m)^/sign\.properties\s*$') {
    Add-Blocker 'sign.properties is not repository-ignored'
}

$hostApiLockPath = Join-Path $repoRoot 'locks/host-api-aars.lock'
$hostApiLock = Read-UniqueProperties $hostApiLockPath
$hostApiLockRaw = if (Test-Path -LiteralPath $hostApiLockPath -PathType Leaf) {
    Get-Content -Raw -LiteralPath $hostApiLockPath -Encoding UTF8
} else {
    ''
}
if ($hostApiLockRaw -match '(?im)^#\s*Host HEAD:.*\bdirty\b') {
    Add-Blocker 'Host API AAR lock identifies a dirty source tree'
}
if ($hostApiLockRaw -notmatch '(?im)^#\s*Host HEAD:\s*[0-9a-f]{40,64}\s+\((?:clean current tree|clean source tree)\)\s*$') {
    Add-Blocker 'Host API AAR lock has no explicit clean Host HEAD identity'
}
if ($hostApiLockRaw -notmatch '(?im)^#\s*Host source fingerprint:\s*[0-9a-f]{64}\s*$') {
    Add-Blocker 'Host API AAR lock has no source fingerprint'
}
if ($hostApiLockRaw -notmatch '(?im)^#\s*Distribution manifest SHA-256:\s*[0-9a-f]{64}\s*$') {
    Add-Blocker 'Host API AAR lock has no distribution manifest SHA-256'
}
if ($hostApiLock['format'] -cne '1') {
    Add-Blocker 'Host API AAR lock format is not 1'
}
$hostApiIds = @('common-plugin-api', 'protocol-wire-api', 'python-runtime-api')
$expectedHostApiLockKeys = @('format')
foreach ($id in $hostApiIds) {
    $expectedHostApiLockKeys += @("$id.file", "$id.sha256")
}
$unexpectedHostApiLockKeys = @(
    $hostApiLock.Keys | Where-Object { $expectedHostApiLockKeys -cnotcontains [string] $_ }
)
$missingHostApiLockKeys = @(
    $expectedHostApiLockKeys | Where-Object { -not $hostApiLock.ContainsKey($_) }
)
if ($unexpectedHostApiLockKeys.Count -ne 0 -or $missingHostApiLockKeys.Count -ne 0) {
    Add-Blocker 'Host API AAR lock inventory must contain exactly common-plugin-api, protocol-wire-api, and python-runtime-api file/SHA-256 pairs'
}
foreach ($id in $hostApiIds) {
    $fileName = $hostApiLock["$id.file"]
    $expectedHash = $hostApiLock["$id.sha256"]
    if (
        [string]::IsNullOrWhiteSpace($fileName) -or
        $fileName -cne [IO.Path]::GetFileName($fileName) -or
        [IO.Path]::GetExtension($fileName) -cne '.aar' -or
        $fileName -match '-debug\.aar$'
    ) {
        Add-Blocker "Invalid locked AAR filename for $id"
        continue
    }
    $aarPath = Join-Path $repoRoot "libs/$fileName"
    if (-not (Test-Path -LiteralPath $aarPath -PathType Leaf)) {
        Add-Blocker "Locked AAR is missing for $id"
    } elseif ($expectedHash -notmatch '^[0-9a-f]{64}$' -or (Get-Sha256 $aarPath) -ne $expectedHash) {
        Add-Blocker "Locked AAR SHA-256 mismatch for $id"
    }
}

$runtimeLock = Read-UniqueProperties (Join-Path $repoRoot 'locks/python-runtime.lock')
$artifactCount = 0
if ($runtimeLock['runtime.artifacts.state'] -ne 'RESOLVED') {
    Add-Blocker 'Python runtime artifact inventory is not RESOLVED'
}
if (-not [int]::TryParse($runtimeLock['runtime.artifacts.count'], [ref] $artifactCount) -or $artifactCount -le 0) {
    Add-Blocker 'Python runtime artifact inventory is empty'
}
if ($runtimeLock['runtime.artifacts.inventory.sha256'] -notmatch '^[0-9a-f]{64}$') {
    Add-Blocker 'Python runtime inventory SHA-256 is invalid'
}

$noticeRoot = Join-Path $repoRoot 'THIRD_PARTY_NOTICES.md'
$noticeAsset = Join-Path $repoRoot 'app/src/main/assets/THIRD_PARTY_NOTICES.md'
if (-not (Test-Path -LiteralPath $noticeRoot -PathType Leaf) -or
    -not (Test-Path -LiteralPath $noticeAsset -PathType Leaf) -or
    (Get-Sha256 $noticeRoot) -ne (Get-Sha256 $noticeAsset)) {
    Add-Blocker 'Root and packaged THIRD_PARTY_NOTICES.md files are absent or different'
}
foreach ($license in @(
    'app/src/main/assets/third_party_licenses/Chaquopy-17.0.0-LICENSE.txt',
    'app/src/main/assets/third_party_licenses/CPython-3.13.9-LICENSE.txt'
)) {
    if (-not (Test-Path -LiteralPath (Join-Path $repoRoot $license) -PathType Leaf)) {
        Add-Blocker "Packaged third-party license is missing: $license"
    }
}

if ($blockers.Count -gt 0) {
    Write-Output 'R6_P2_RELEASE_SOURCE_GATE=BLOCKED'
    foreach ($blocker in $blockers) {
        Write-Output "BLOCKER=$blocker"
    }
    exit 2
}

Write-Output "R6_P2_RELEASE_SOURCE_GATE=PASS version=$versionName versionCode=$versionBuild"
