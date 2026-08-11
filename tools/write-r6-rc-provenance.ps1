[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $HostRepo,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $HostApk,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $PluginArm64Apk,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $PluginX8664Apk,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $PluginUniversalApk,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $CommonPluginApiAar,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $ProtocolWireApiAar,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $PythonRuntimeApiAar,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $Aapt2,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $ApkSigner,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $Output
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$pluginRepo = [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$pinnedHostPackage = 'org.autojs.autojs6'
$pinnedPluginPackage = 'io.github.supermonster003.autojs6.plugin.python.runtime'
$pinnedReleaseKeystoreSha256 = '0d6b79e4d4efe77829dbcc2e21096931ba7b0349df82f3b58c3e9d24e84f1df0'
$pinnedReleaseCertificateSha256 = '31a681fcfffb3e428420cae280ded89292b12a3b0f59e19b7a73e32a8ae4c213'
$declaredPluginAbis = @('arm64-v8a', 'x86_64')
$sha256Pattern = '^[0-9a-f]{64}$'
$git = (Get-Command git -CommandType Application -ErrorAction Stop).Source

function Assert-True([bool] $Condition, [string] $Message) {
    if (-not $Condition) {
        throw $Message
    }
}

function Resolve-ExistingDirectory([string] $Path, [string] $Label) {
    $fullPath = [IO.Path]::GetFullPath($Path)
    Assert-True (Test-Path -LiteralPath $fullPath -PathType Container) "$Label is not an existing directory"
    return $fullPath
}

function Resolve-ExistingFile([string] $Path, [string] $Label) {
    $fullPath = [IO.Path]::GetFullPath($Path)
    Assert-True (Test-Path -LiteralPath $fullPath -PathType Leaf) "$Label is not an existing file"
    $item = Get-Item -LiteralPath $fullPath
    Assert-True ($item.Length -gt 0) "$Label is empty"
    return $item.FullName
}

function Invoke-NativeCapture(
    [string] $FilePath,
    [string[]] $Arguments,
    [string] $Label,
    [int[]] $AcceptedExitCodes = @(0)
) {
    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $outputLines = & $FilePath @Arguments 2>&1
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
    $outputText = (($outputLines | Out-String).Trim())
    if ($AcceptedExitCodes -notcontains $exitCode) {
        $detail = if ($outputText.Length -gt 0) { ": $outputText" } else { '' }
        throw "$Label failed with exit code $exitCode$detail"
    }
    return $outputText
}

function Invoke-Git([string] $Repo, [string[]] $Arguments, [string] $Label) {
    return Invoke-NativeCapture $git (@('-C', $Repo) + $Arguments) $Label
}

function Read-UniqueProperties([string] $Path, [string] $Label) {
    Assert-True (Test-Path -LiteralPath $Path -PathType Leaf) "$Label is missing"
    $properties = @{}
    $lineNumber = 0
    foreach ($rawLine in Get-Content -LiteralPath $Path -Encoding UTF8) {
        $lineNumber++
        $line = $rawLine.Trim()
        if ($line.Length -eq 0 -or $line.StartsWith('#') -or $line.StartsWith('!')) {
            continue
        }
        $separator = $line.IndexOf('=')
        Assert-True ($separator -gt 0) "$Label contains a malformed property at line $lineNumber"
        $key = $line.Substring(0, $separator).Trim()
        $value = $line.Substring($separator + 1).Trim()
        Assert-True (-not $properties.ContainsKey($key)) "$Label contains duplicate property $key"
        $properties[$key] = $value
    }
    return $properties
}

function Get-RequiredProperty([hashtable] $Properties, [string] $Key, [string] $Label) {
    Assert-True ($Properties.ContainsKey($Key)) "$Label is missing property $Key"
    $value = [string] $Properties[$Key]
    Assert-True (-not [string]::IsNullOrWhiteSpace($value)) "$Label contains an empty property $Key"
    return $value
}

function Get-Sha256([string] $Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Get-Utf8Sha256([string] $Value) {
    $bytes = [Text.Encoding]::UTF8.GetBytes($Value)
    $algorithm = [Security.Cryptography.SHA256]::Create()
    try {
        return (($algorithm.ComputeHash($bytes) | ForEach-Object { $_.ToString('x2') }) -join '')
    } finally {
        $algorithm.Dispose()
    }
}

function New-FileRecord([string] $Path) {
    $item = Get-Item -LiteralPath $Path
    return [ordered]@{
        path = $item.FullName
        sizeBytes = [long] $item.Length
        sha256 = Get-Sha256 $item.FullName
    }
}

function Get-RepositoryIdentity([string] $Repo, [string] $Label) {
    $topLevel = Invoke-Git $Repo @('rev-parse', '--show-toplevel') "$Label Git root inspection"
    Assert-True (
        [IO.Path]::GetFullPath($topLevel).Equals($Repo, [StringComparison]::OrdinalIgnoreCase)
    ) "$Label path is not its Git top-level directory"

    $head = (Invoke-Git $Repo @('rev-parse', '--verify', 'HEAD') "$Label Git HEAD inspection").ToLowerInvariant()
    Assert-True ($head -match '^[0-9a-f]{40,64}$') "$Label Git HEAD is not a full commit identity"
    $commitCountText = Invoke-Git $Repo @('rev-list', '--count', 'HEAD') "$Label Git commit-count inspection"
    $commitCount = 0
    Assert-True ([int]::TryParse($commitCountText, [ref] $commitCount) -and $commitCount -gt 0) "$Label Git commit count is invalid"
    $status = Invoke-Git $Repo @('status', '--porcelain', '--untracked-files=all') "$Label Git status inspection"
    Assert-True ($status.Length -eq 0) "$Label Git worktree is not clean"
    $branch = Invoke-Git $Repo @('rev-parse', '--abbrev-ref', 'HEAD') "$Label Git branch inspection"

    return [ordered]@{
        root = $Repo
        commit = $head
        commitCount = $commitCount
        branch = $branch
        clean = $true
    }
}

function Get-ApkInfo([string] $Path, [string] $Role) {
    $badging = Invoke-NativeCapture $Aapt2 @('dump', 'badging', $Path) "$Role aapt2 inspection"
    $packageMatch = [regex]::Match(
        $badging,
        "(?m)^package:\s+name='([^']+)'\s+versionCode='([0-9]+)'\s+versionName='([^']*)'.*$"
    )
    Assert-True $packageMatch.Success "$Role has no parseable package/version badging"
    # aapt2 36.1 emits minSdkVersion while older aapt variants emit sdkVersion.
    # Both names represent the same manifest minSdk field.
    $sdkMatch = [regex]::Match($badging, "(?m)^(?:minSdkVersion|sdkVersion):'([^']+)'\s*$")
    $targetSdkMatch = [regex]::Match($badging, "(?m)^targetSdkVersion:'([^']+)'\s*$")
    $compileSdkMatch = [regex]::Match($packageMatch.Value, "compileSdkVersion='([^']+)'")
    Assert-True ($sdkMatch.Success -and $targetSdkMatch.Success -and $compileSdkMatch.Success) "$Role SDK badging is incomplete"

    $nativeLine = [regex]::Match($badging, '(?m)^native-code:\s*(.+?)\s*$')
    Assert-True $nativeLine.Success "$Role does not declare a native ABI"
    $abis = @(
        [regex]::Matches($nativeLine.Groups[1].Value, "'([^']+)'") |
            ForEach-Object { $_.Groups[1].Value } |
            Sort-Object -Unique
    )
    Assert-True ($abis.Count -gt 0) "$Role native ABI list is empty"
    Assert-True ($badging -notmatch '(?m)^application-debuggable\s*$') "$Role is debuggable and is not a Release Candidate artifact"

    $signing = Invoke-NativeCapture $ApkSigner @('verify', '--verbose', '--print-certs', $Path) "$Role apksigner verification"
    Assert-True (
        $signing -match '(?m)^Verified using v2 scheme \(APK Signature Scheme v2\): true\s*$'
    ) "$Role is not verified with APK Signature Scheme v2"
    $signers = @(
        [regex]::Matches(
            $signing,
            '(?m)^Signer #[0-9]+ certificate SHA-256 digest:\s*([0-9a-fA-F]{64})\s*$'
        ) |
            ForEach-Object { $_.Groups[1].Value.ToLowerInvariant() } |
            Sort-Object -Unique
    )
    Assert-True ($signers.Count -gt 0) "$Role has no parseable signer certificate SHA-256"

    $versionCode = 0L
    Assert-True ([long]::TryParse($packageMatch.Groups[2].Value, [ref] $versionCode)) "$Role versionCode is invalid"
    return [ordered]@{
        role = $Role
        file = New-FileRecord $Path
        packageName = $packageMatch.Groups[1].Value
        versionCode = $versionCode
        versionName = $packageMatch.Groups[3].Value
        minSdk = $sdkMatch.Groups[1].Value
        targetSdk = $targetSdkMatch.Groups[1].Value
        compileSdk = $compileSdkMatch.Groups[1].Value
        abis = $abis
        signerSha256 = $signers
        v2Verified = $true
        debuggable = $false
    }
}

function Assert-ExactStringSet([object[]] $Actual, [string[]] $Expected, [string] $Label) {
    $actualNormalized = @($Actual | ForEach-Object { [string] $_ } | Sort-Object -Unique)
    $expectedNormalized = @($Expected | Sort-Object -Unique)
    $difference = @(Compare-Object -ReferenceObject $expectedNormalized -DifferenceObject $actualNormalized)
    Assert-True ($difference.Count -eq 0) "$Label differs from the expected exact set"
}

function Assert-PackageVersion(
    [System.Collections.IDictionary] $ApkInfo,
    [string] $ExpectedPackage,
    [hashtable] $VersionProperties,
    [string] $Label
) {
    $expectedVersionName = Get-RequiredProperty $VersionProperties 'VERSION_NAME' "$Label version.properties"
    $expectedVersionCode = 0L
    Assert-True (
        [long]::TryParse(
            (Get-RequiredProperty $VersionProperties 'VERSION_BUILD' "$Label version.properties"),
            [ref] $expectedVersionCode
        )
    ) "$Label VERSION_BUILD is invalid"
    Assert-True ($ApkInfo.packageName -ceq $ExpectedPackage) "$Label package name differs from the frozen package"
    Assert-True ($ApkInfo.versionName -ceq $expectedVersionName) "$Label versionName differs from version.properties"
    Assert-True ($ApkInfo.versionCode -eq $expectedVersionCode) "$Label versionCode differs from version.properties"
    Assert-True (
        $ApkInfo.minSdk -ceq (Get-RequiredProperty $VersionProperties 'MIN_SDK_VERSION' "$Label version.properties")
    ) "$Label minSdk differs from version.properties"
    Assert-True (
        $ApkInfo.targetSdk -ceq (Get-RequiredProperty $VersionProperties 'TARGET_SDK_VERSION' "$Label version.properties")
    ) "$Label targetSdk differs from version.properties"
    Assert-True (
        $ApkInfo.compileSdk -ceq (Get-RequiredProperty $VersionProperties 'COMPILE_SDK_VERSION' "$Label version.properties")
    ) "$Label compileSdk differs from version.properties"
}

function Assert-ApkFileName(
    [string] $Path,
    [string] $Prefix,
    [string] $VersionName,
    [string] $Architecture,
    [string] $Label
) {
    $normalizedVersion = [regex]::Replace($VersionName.Trim(), '\s+', '-').ToLowerInvariant()
    $expectedName = "$Prefix-v$normalizedVersion-$Architecture.apk".ToLowerInvariant()
    Assert-True (
        [IO.Path]::GetFileName($Path).Equals($expectedName, [StringComparison]::OrdinalIgnoreCase)
    ) "$Label filename is not the deterministic version/ABI release name"
}

function Get-ReleaseIdentityLockRecord([string] $Path) {
    $properties = Read-UniqueProperties $Path 'Release identity lock'
    $expected = [ordered]@{
        'format' = '1'
        'host.package' = $pinnedHostPackage
        'plugin.package' = $pinnedPluginPackage
        'release.keystore.sha256' = $pinnedReleaseKeystoreSha256
        'release.certificate.sha256' = $pinnedReleaseCertificateSha256
    }
    Assert-True ($properties.Count -eq $expected.Count) 'Release identity lock contains missing or unexpected keys'
    foreach ($entry in $expected.GetEnumerator()) {
        Assert-True ($properties[$entry.Key] -ceq $entry.Value) "Release identity lock mismatch for $($entry.Key)"
    }
    foreach ($key in $properties.Keys) {
        Assert-True (@($expected.Keys) -ccontains [string] $key) "Release identity lock contains unexpected key: $key"
    }

    return [ordered]@{
        file = New-FileRecord $Path
        format = '1'
        hostPackage = $properties['host.package']
        pluginPackage = $properties['plugin.package']
        keystoreSha256 = $properties['release.keystore.sha256']
        certificateSha256 = $properties['release.certificate.sha256']
    }
}

function Get-RuntimeLockRecord([string] $Path) {
    $properties = Read-UniqueProperties $Path 'Python runtime lock'
    Assert-True ((Get-RequiredProperty $properties 'format' 'Python runtime lock') -ceq '2') 'Python runtime lock format is not 2'
    Assert-True (
        (Get-RequiredProperty $properties 'runtime.artifacts.state' 'Python runtime lock') -ceq 'RESOLVED'
    ) 'Python runtime artifact inventory is not RESOLVED'
    Assert-True (
        (Get-RequiredProperty $properties 'android.abis' 'Python runtime lock') -ceq 'arm64-v8a,x86_64'
    ) 'Python runtime lock ABI declaration drifted'

    $count = 0
    Assert-True (
        [int]::TryParse(
            (Get-RequiredProperty $properties 'runtime.artifacts.count' 'Python runtime lock'),
            [ref] $count
        ) -and $count -gt 0
    ) 'Python runtime artifact count is invalid'

    $inventory = [System.Collections.Generic.List[object]]::new()
    $canonical = [Text.StringBuilder]::new()
    $expectedArtifactKeys = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    for ($index = 0; $index -lt $count; $index++) {
        $ordinal = $index.ToString('000')
        $prefix = "runtime.artifact.$ordinal"
        $coordinateKey = "$prefix.coordinate"
        $fileKey = "$prefix.file"
        $shaKey = "$prefix.sha256"
        [void] $expectedArtifactKeys.Add($coordinateKey)
        [void] $expectedArtifactKeys.Add($fileKey)
        [void] $expectedArtifactKeys.Add($shaKey)
        $coordinate = Get-RequiredProperty $properties $coordinateKey 'Python runtime lock'
        $fileName = Get-RequiredProperty $properties $fileKey 'Python runtime lock'
        $sha256 = (Get-RequiredProperty $properties $shaKey 'Python runtime lock').ToLowerInvariant()
        Assert-True ($fileName -ceq [IO.Path]::GetFileName($fileName)) "Python runtime lock file $ordinal is not a basename"
        Assert-True ($sha256 -match $sha256Pattern) "Python runtime lock SHA-256 $ordinal is invalid"
        [void] $canonical.Append("$ordinal|$coordinate|$fileName|$sha256`n")
        $inventory.Add([ordered]@{
            ordinal = $ordinal
            coordinate = $coordinate
            file = $fileName
            sha256 = $sha256
        })
    }
    $actualArtifactKeys = @($properties.Keys | Where-Object { $_ -like 'runtime.artifact.*' })
    Assert-True ($actualArtifactKeys.Count -eq $expectedArtifactKeys.Count) 'Python runtime lock artifact key count drifted'
    foreach ($key in $actualArtifactKeys) {
        Assert-True ($expectedArtifactKeys.Contains([string] $key)) 'Python runtime lock has an unexpected artifact key'
    }

    $declaredInventorySha256 = (
        Get-RequiredProperty $properties 'runtime.artifacts.inventory.sha256' 'Python runtime lock'
    ).ToLowerInvariant()
    Assert-True ($declaredInventorySha256 -match $sha256Pattern) 'Python runtime inventory SHA-256 is invalid'
    Assert-True (
        (Get-Utf8Sha256 $canonical.ToString()) -ceq $declaredInventorySha256
    ) 'Python runtime canonical inventory SHA-256 mismatch'

    return [ordered]@{
        file = New-FileRecord $Path
        state = 'RESOLVED'
        artifactCount = $count
        inventorySha256 = $declaredInventorySha256
        pythonVersion = Get-RequiredProperty $properties 'python.version.expected' 'Python runtime lock'
        chaquopyVersion = Get-RequiredProperty $properties 'chaquopy.plugin.version' 'Python runtime lock'
        abis = $declaredPluginAbis
        artifacts = @($inventory)
    }
}

function Get-HostApiLockRecord(
    [string] $Path,
    [string] $HostCommit,
    [string] $CommonAar,
    [string] $ProtocolAar,
    [string] $PythonAar
) {
    $properties = Read-UniqueProperties $Path 'Host API AAR lock'
    Assert-True ((Get-RequiredProperty $properties 'format' 'Host API AAR lock') -ceq '1') 'Host API AAR lock format is not 1'
    $hostApiEntries = @(
        [ordered]@{ id = 'common-plugin-api'; path = $CommonAar },
        [ordered]@{ id = 'protocol-wire-api'; path = $ProtocolAar },
        [ordered]@{ id = 'python-runtime-api'; path = $PythonAar }
    )
    $hostApiIds = @($hostApiEntries | ForEach-Object { [string] $_.id })
    $expectedHostApiLockKeys = @('format')
    foreach ($id in $hostApiIds) {
        $expectedHostApiLockKeys += @("$id.file", "$id.sha256")
    }
    $unexpectedHostApiLockKeys = @(
        $properties.Keys | Where-Object { $expectedHostApiLockKeys -cnotcontains [string] $_ }
    )
    $missingHostApiLockKeys = @(
        $expectedHostApiLockKeys | Where-Object { -not $properties.ContainsKey($_) }
    )
    Assert-True (
        $unexpectedHostApiLockKeys.Count -eq 0 -and $missingHostApiLockKeys.Count -eq 0
    ) 'Host API AAR lock inventory must contain exactly common-plugin-api, protocol-wire-api, and python-runtime-api file/SHA-256 pairs'
    $rawLock = Get-Content -Raw -LiteralPath $Path -Encoding UTF8
    Assert-True ($rawLock -notmatch '(?im)dirty current tree') 'Host API AAR lock still identifies a dirty source tree'
    $hostHeadMatch = [regex]::Match(
        $rawLock,
        '(?im)^#\s*Host HEAD:\s*([0-9a-f]{40,64})(?:\s+\((?:clean current tree|clean source tree)\))?\s*$'
    )
    $sourceFingerprintMatch = [regex]::Match($rawLock, '(?im)^#\s*Host source fingerprint:\s*([0-9a-f]{64})\s*$')
    $manifestShaMatch = [regex]::Match($rawLock, '(?im)^#\s*Distribution manifest SHA-256:\s*([0-9a-f]{64})\s*$')
    Assert-True $hostHeadMatch.Success 'Host API AAR lock has no clean Host HEAD identity'
    Assert-True $sourceFingerprintMatch.Success 'Host API AAR lock has no source fingerprint'
    Assert-True $manifestShaMatch.Success 'Host API AAR lock has no distribution manifest SHA-256'
    Assert-True (
        $hostHeadMatch.Groups[1].Value.Equals($HostCommit, [StringComparison]::OrdinalIgnoreCase)
    ) 'Host API AAR lock Host HEAD differs from the frozen host commit'

    $records = [ordered]@{}
    foreach ($entry in $hostApiEntries) {
        $id = [string] $entry.id
        $aarPath = [string] $entry.path
        $lockedFile = Get-RequiredProperty $properties "$id.file" 'Host API AAR lock'
        $lockedSha256 = (Get-RequiredProperty $properties "$id.sha256" 'Host API AAR lock').ToLowerInvariant()
        Assert-True ($lockedFile -ceq [IO.Path]::GetFileName($aarPath)) "Host API AAR lock filename mismatch for $id"
        Assert-True ([IO.Path]::GetExtension($lockedFile) -ceq '.aar') "Host API AAR lock filename is not an AAR for $id"
        Assert-True ($lockedFile -notmatch '-debug\.aar$') "Host API AAR lock points to a debug AAR for $id"
        Assert-True ($lockedSha256 -match $sha256Pattern) "Host API AAR lock SHA-256 is invalid for $id"
        $fileRecord = New-FileRecord $aarPath
        Assert-True ($fileRecord.sha256 -ceq $lockedSha256) "Host API AAR SHA-256 mismatch for $id"
        $records[$id] = $fileRecord
    }

    return [ordered]@{
        file = New-FileRecord $Path
        hostCommit = $hostHeadMatch.Groups[1].Value.ToLowerInvariant()
        sourceFingerprint = $sourceFingerprintMatch.Groups[1].Value.ToLowerInvariant()
        distributionManifestSha256 = $manifestShaMatch.Groups[1].Value.ToLowerInvariant()
        aars = $records
    }
}

$HostRepo = Resolve-ExistingDirectory $HostRepo 'Host repository'
$HostApk = Resolve-ExistingFile $HostApk 'Host APK'
$PluginArm64Apk = Resolve-ExistingFile $PluginArm64Apk 'Plugin arm64-v8a APK'
$PluginX8664Apk = Resolve-ExistingFile $PluginX8664Apk 'Plugin x86_64 APK'
$PluginUniversalApk = Resolve-ExistingFile $PluginUniversalApk 'Plugin universal APK'
$CommonPluginApiAar = Resolve-ExistingFile $CommonPluginApiAar 'Common Plugin API AAR'
$ProtocolWireApiAar = Resolve-ExistingFile $ProtocolWireApiAar 'Protocol Wire API AAR'
$PythonRuntimeApiAar = Resolve-ExistingFile $PythonRuntimeApiAar 'Python Runtime API AAR'
$Aapt2 = Resolve-ExistingFile $Aapt2 'aapt2'
$ApkSigner = Resolve-ExistingFile $ApkSigner 'apksigner'
Assert-True ([IO.Path]::GetFileName($Aapt2) -ieq 'aapt2.exe') 'Aapt2 must identify aapt2.exe explicitly'
Assert-True (
    [IO.Path]::GetFileName($ApkSigner) -in @('apksigner.bat', 'apksigner.exe')
) 'ApkSigner must identify apksigner.bat or apksigner.exe explicitly'

$reportsRoot = [IO.Path]::GetFullPath((Join-Path $pluginRepo 'build/reports'))
$reportsRootPrefix = $reportsRoot.TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
$outputPath = if ([IO.Path]::IsPathRooted($Output)) {
    [IO.Path]::GetFullPath($Output)
} else {
    [IO.Path]::GetFullPath((Join-Path $pluginRepo $Output))
}
Assert-True (
    $outputPath.StartsWith($reportsRootPrefix, [StringComparison]::OrdinalIgnoreCase)
) 'Output must be a file below the plugin build/reports directory'
Assert-True ([IO.Path]::GetExtension($outputPath) -ceq '.json') 'Output must use the .json extension'
$relativeOutput = $outputPath.Substring($pluginRepo.TrimEnd('\', '/').Length).TrimStart('\', '/').Replace('\', '/')
[void] (Invoke-NativeCapture $git @('-C', $pluginRepo, 'check-ignore', '--quiet', '--no-index', '--', $relativeOutput) 'Output ignore-policy inspection')

$hostIdentity = Get-RepositoryIdentity $HostRepo 'Host repository'
$pluginIdentity = Get-RepositoryIdentity $pluginRepo 'Plugin repository'
$releaseIdentityLockPath = Join-Path $pluginRepo 'locks/release-identity.lock'
$releaseIdentityLockRecord = Get-ReleaseIdentityLockRecord $releaseIdentityLockPath
$expectedHostPackage = $releaseIdentityLockRecord.hostPackage
$expectedPluginPackage = $releaseIdentityLockRecord.pluginPackage
$hostVersionProperties = Read-UniqueProperties (Join-Path $HostRepo 'version.properties') 'Host version.properties'
$pluginVersionProperties = Read-UniqueProperties (Join-Path $pluginRepo 'version.properties') 'Plugin version.properties'
$pluginVersionBuild = 0
Assert-True (
    [int]::TryParse(
        (Get-RequiredProperty $pluginVersionProperties 'VERSION_BUILD' 'Plugin version.properties'),
        [ref] $pluginVersionBuild
    )
) 'Plugin VERSION_BUILD is invalid'
Assert-True (
    $pluginVersionBuild -eq $pluginIdentity.commitCount
) 'Plugin VERSION_BUILD must equal the clean repository commit count'

$hostApkInfo = Get-ApkInfo $HostApk 'host'
$pluginArm64Info = Get-ApkInfo $PluginArm64Apk 'plugin-arm64-v8a'
$pluginX8664Info = Get-ApkInfo $PluginX8664Apk 'plugin-x86_64'
$pluginUniversalInfo = Get-ApkInfo $PluginUniversalApk 'plugin-universal'
Assert-PackageVersion $hostApkInfo $expectedHostPackage $hostVersionProperties 'Host APK'
foreach ($pluginApkInfo in @($pluginArm64Info, $pluginX8664Info, $pluginUniversalInfo)) {
    Assert-PackageVersion $pluginApkInfo $expectedPluginPackage $pluginVersionProperties $pluginApkInfo.role
}
Assert-True ($hostApkInfo.abis.Count -eq 1) 'Host APK must be one exact arm64-v8a or x86_64 split'
Assert-True ($declaredPluginAbis -ccontains $hostApkInfo.abis[0]) 'Host APK ABI is outside the Python RC ABI declaration'
Assert-ExactStringSet $pluginArm64Info.abis @('arm64-v8a') 'Plugin arm64-v8a APK ABI set'
Assert-ExactStringSet $pluginX8664Info.abis @('x86_64') 'Plugin x86_64 APK ABI set'
Assert-ExactStringSet $pluginUniversalInfo.abis $declaredPluginAbis 'Plugin universal APK ABI set'
$hostVersionName = Get-RequiredProperty $hostVersionProperties 'VERSION_NAME' 'Host version.properties'
$pluginVersionName = Get-RequiredProperty $pluginVersionProperties 'VERSION_NAME' 'Plugin version.properties'
Assert-ApkFileName $HostApk 'autojs6' $hostVersionName $hostApkInfo.abis[0] 'Host APK'
Assert-ApkFileName $PluginArm64Apk 'autojs6-plugin-python-runtime' $pluginVersionName 'arm64-v8a' 'Plugin arm64-v8a APK'
Assert-ApkFileName $PluginX8664Apk 'autojs6-plugin-python-runtime' $pluginVersionName 'x86_64' 'Plugin x86_64 APK'
Assert-ApkFileName $PluginUniversalApk 'autojs6-plugin-python-runtime' $pluginVersionName 'universal' 'Plugin universal APK'

$allApkInfos = @($hostApkInfo, $pluginArm64Info, $pluginX8664Info, $pluginUniversalInfo)
foreach ($apkInfo in $allApkInfos) {
    $apkSigners = @($apkInfo.signerSha256)
    Assert-True ($apkSigners.Count -eq 1) "$($apkInfo.role) signer set is not an exact singleton"
    Assert-True (
        $apkSigners[0] -ceq $releaseIdentityLockRecord.certificateSha256
    ) "$($apkInfo.role) signer differs from the release identity pin"
    Assert-ExactStringSet $apkSigners @($releaseIdentityLockRecord.certificateSha256) "$($apkInfo.role) signer set"
}
$referenceSigners = @($releaseIdentityLockRecord.certificateSha256)
$signerSetSha256 = Get-Utf8Sha256 ((@($referenceSigners | Sort-Object) -join "`n") + "`n")

$hostApiLockPath = Join-Path $pluginRepo 'locks/host-api-aars.lock'
$runtimeLockPath = Join-Path $pluginRepo 'locks/python-runtime.lock'
$hostApiLockRecord = Get-HostApiLockRecord `
    $hostApiLockPath `
    $hostIdentity.commit `
    $CommonPluginApiAar `
    $ProtocolWireApiAar `
    $PythonRuntimeApiAar
$runtimeLockRecord = Get-RuntimeLockRecord $runtimeLockPath

$aapt2Version = Invoke-NativeCapture $Aapt2 @('version') 'aapt2 version inspection'
$apkSignerVersion = Invoke-NativeCapture $ApkSigner @('version') 'apksigner version inspection'
$claims = [ordered]@{
    evidenceLevel = 'RELEASE_CANDIDATE_LOCAL'
    published = $false
    deviceValidated = $false
    p3Validated = $false
}
$report = [ordered]@{
    schemaVersion = 1
    createdAtUtc = [DateTimeOffset]::UtcNow.ToString('o')
    claims = $claims
    repositories = [ordered]@{
        host = $hostIdentity
        plugin = $pluginIdentity
    }
    compatibility = [ordered]@{
        hostPackage = $expectedHostPackage
        pluginPackage = $expectedPluginPackage
        protocolMin = '1.0'
        protocolMax = '1.1'
        declaredPluginAbis = $declaredPluginAbis
    }
    apks = [ordered]@{
        host = $hostApkInfo
        pluginArm64 = $pluginArm64Info
        pluginX8664 = $pluginX8664Info
        pluginUniversal = $pluginUniversalInfo
        exactSignerSetSha256 = $signerSetSha256
    }
    buildInputs = [ordered]@{
        releaseIdentity = $releaseIdentityLockRecord
        hostApiDistribution = $hostApiLockRecord
        pythonRuntime = $runtimeLockRecord
        tools = [ordered]@{
            aapt2 = [ordered]@{
                file = New-FileRecord $Aapt2
                version = $aapt2Version
            }
            apkSigner = [ordered]@{
                file = New-FileRecord $ApkSigner
                version = $apkSignerVersion
            }
        }
    }
}

$outputDirectory = [IO.Path]::GetDirectoryName($outputPath)
[void] (New-Item -ItemType Directory -Path $outputDirectory -Force)
$temporaryPath = Join-Path $outputDirectory ('.' + [IO.Path]::GetFileName($outputPath) + '.' + [Guid]::NewGuid().ToString('N') + '.tmp')
$utf8WithoutBom = [Text.UTF8Encoding]::new($false)
try {
    $json = ($report | ConvertTo-Json -Depth 16) + "`n"
    [IO.File]::WriteAllText($temporaryPath, $json, $utf8WithoutBom)
    if (Test-Path -LiteralPath $outputPath -PathType Leaf) {
        [IO.File]::Replace($temporaryPath, $outputPath, $null)
    } else {
        [IO.File]::Move($temporaryPath, $outputPath)
    }
} finally {
    if (Test-Path -LiteralPath $temporaryPath -PathType Leaf) {
        Remove-Item -LiteralPath $temporaryPath -Force
    }
}

$outputSha256 = Get-Sha256 $outputPath
Write-Output "R6_RC_PROVENANCE=RELEASE_CANDIDATE_LOCAL"
Write-Output "OUTPUT=$outputPath"
Write-Output "OUTPUT_SHA256=$outputSha256"
Write-Output "HOST_COMMIT=$($hostIdentity.commit)"
Write-Output "PLUGIN_COMMIT=$($pluginIdentity.commit)"
Write-Output "SIGNER_SET_SHA256=$signerSetSha256"
