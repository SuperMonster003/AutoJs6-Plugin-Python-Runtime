#Requires -Version 7.0

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $Provenance,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9A-Fa-f]{64}$')]
    [string] $ProvenanceSha256,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $P3Evidence,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9A-Fa-f]{64}$')]
    [string] $P3EvidenceSha256,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9A-Fa-f]{40,64}$')]
    [string] $ExpectedHostCommit,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9A-Fa-f]{40,64}$')]
    [string] $ExpectedPluginCommit,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9A-Fa-f]{40,64}$')]
    [string] $ResolvedTagCommit,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^v0\.1\.0$')]
    [string] $ReleaseTag,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $ReleaseUrl,

    [Parameter(Mandatory = $true)]
    [long] $ReleaseId,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$')]
    [string] $ReleasePublishedAtUtc,

    [Parameter(Mandatory = $true)]
    [bool] $ReleaseDraft,

    [Parameter(Mandatory = $true)]
    [bool] $ReleasePrerelease,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $LocalArm64Apk,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $LocalX8664Apk,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $LocalUniversalApk,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $DownloadedArm64Apk,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $DownloadedX8664Apk,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $DownloadedUniversalApk,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $RemoteArm64AssetName,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9A-Fa-f]{64}$')]
    [string] $RemoteArm64Sha256,

    [Parameter(Mandatory = $true)]
    [long] $RemoteArm64SizeBytes,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $RemoteX8664AssetName,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9A-Fa-f]{64}$')]
    [string] $RemoteX8664Sha256,

    [Parameter(Mandatory = $true)]
    [long] $RemoteX8664SizeBytes,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $RemoteUniversalAssetName,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9A-Fa-f]{64}$')]
    [string] $RemoteUniversalSha256,

    [Parameter(Mandatory = $true)]
    [long] $RemoteUniversalSizeBytes,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^\S+$')]
    [string] $ExpectedDeviceSerial,

    [Parameter(Mandatory = $true)]
    [ValidateRange(24, 99)]
    [int] $ExpectedDeviceApi,

    [Parameter(Mandatory = $true)]
    [ValidateSet('arm64-v8a')]
    [string] $ExpectedDeviceAbi,

    [Parameter(Mandatory = $true)]
    [int[]] $ExpectedUserIds,

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
$PSNativeCommandUseErrorActionPreference = $false

$pluginRepo = [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$pinnedHostCommit = '2caddcb763b39f0bf450909742fa6ec4caba27a8'
$pinnedHostPackage = 'org.autojs.autojs6'
$pinnedPluginPackage = 'io.github.supermonster003.autojs6.plugin.python.runtime'
$pinnedHostVersionName = '6.8.0'
$pinnedHostVersionCode = 5275L
$pinnedPluginVersionName = '0.1.0'
$pinnedPluginVersionCode = 9L
$pinnedReleaseTag = 'v0.1.0'
$pinnedReleaseUrl = 'https://github.com/SuperMonster003/AutoJs6-Plugin-Python-Runtime/releases/tag/v0.1.0'
$pinnedReleaseKeystoreSha256 = '0d6b79e4d4efe77829dbcc2e21096931ba7b0349df82f3b58c3e9d24e84f1df0'
$pinnedReleaseCertificateSha256 = '31a681fcfffb3e428420cae280ded89292b12a3b0f59e19b7a73e32a8ae4c213'
$pinnedDifferentSignerSha256 = 'a40da80a59d170caa950cf15c18c454d47a39b26989d8b640ecd745ba71bf5dc'
$pinnedHostApiSourceFingerprint = '4de961d6cc8f5df204cf535091179199c73946e945da70efed408794a4ad766b'
$pinnedHostApiDistributionManifestSha256 = '9f296ad45c24b7eb3e217e4d0ce6c96ba2593966b2bed1db1f2846d658987818'
$declaredPluginAbis = @('arm64-v8a', 'x86_64')
$sha256Pattern = '^[0-9a-f]{64}$'
$hostApiDefinitions = [ordered]@{
    'common-plugin-api' = [ordered]@{
        file = 'common-plugin-api.aar'
        sha256 = '6d75eb2350aa56ed412dabf84b34c0f65b9a6f6cfce3f3c23f79b9b198c24a63'
    }
    'protocol-wire-api' = [ordered]@{
        file = 'protocol-wire-api.aar'
        sha256 = 'e044dd3cc9bed84e844174e0963b57a1f67902cf021ccb42d1031d3511ce46da'
    }
    'python-runtime-api' = [ordered]@{
        file = 'python-runtime-api.aar'
        sha256 = 'e42a2c35cfb9bed27c02ad4a781a1b4bf7f5766d78a46ad194675f090c1c0127'
    }
}

$availabilityTest = 'org.autojs.autojs.core.plugin.python.PythonRuntimeR6ProviderAvailabilityInstrumentationTest#productionClientMatchesExplicitProviderAvailabilityPhase'
$cancelRebindTest = 'org.autojs.autojs.core.plugin.python.PythonRuntimeRealPluginCancelRebindDiagnosticTest#cancelAfterStartedKillsOldBinderThenExactRebindRunsFiniteRequestOnce'
$timeoutRebindTest = 'org.autojs.autojs.core.plugin.python.PythonRuntimeRealPluginTimeoutRebindDiagnosticTest#providerTimeoutFailsBeforeOldBinderDeathThenExactRebindRunsFiniteRequest'
$sessionRelayTest = 'org.autojs.autojs.core.plugin.python.PythonRuntimeR6SessionRelayInstrumentationTest#alternateUidCannotMutateRelayedSessionAndOwnerStillCompletesExactlyOnce'
$sameSignerTest = 'org.autojs.plugin.python.runtime.consumer.PythonRuntimeSameSignerDifferentUidAndroidTest#sameSignerDifferentUidIsRejectedAtEveryProviderEntry'
$differentSignerTest = 'org.autojs.plugin.python.runtime.consumer.PythonRuntimeSameSignerDifferentUidAndroidTest#differentSignerCannotAcquirePluginPermissionOrBindProvider'

function Assert-True([bool] $Condition, [string] $Message) {
    if (-not $Condition) {
        throw $Message
    }
}

function Resolve-ExistingFile([string] $Path, [string] $Label) {
    $resolved = @(Resolve-Path -LiteralPath $Path -ErrorAction Stop)
    Assert-True ($resolved.Count -eq 1) "$Label must resolve to exactly one file"
    $item = Get-Item -LiteralPath $resolved[0].ProviderPath -Force
    Assert-True (-not $item.PSIsContainer) "$Label is not a file"
    Assert-True ($item.Length -gt 0) "$Label is empty"
    return $item.FullName
}

function Get-Sha256([string] $Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Normalize-Sha256([string] $Value, [string] $Label) {
    $normalized = $Value.ToLowerInvariant()
    Assert-True ($normalized -match $sha256Pattern) "$Label is not a SHA-256 value"
    return $normalized
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
    $item = Get-Item -LiteralPath $Path -Force
    return [ordered]@{
        path = $item.FullName
        sizeBytes = [long] $item.Length
        sha256 = Get-Sha256 $item.FullName
    }
}

function Get-RequiredMember([object] $Object, [string] $Name, [string] $Label) {
    Assert-True ($null -ne $Object) "$Label is null"
    $property = $Object.PSObject.Properties[$Name]
    Assert-True ($null -ne $property) "$Label is missing property $Name"
    return $property.Value
}

function Assert-ExactObjectKeys([object] $Object, [string[]] $Expected, [string] $Label) {
    Assert-True ($null -ne $Object) "$Label is null"
    $actual = @($Object.PSObject.Properties.Name | Sort-Object -Unique)
    $expectedNormalized = @($Expected | Sort-Object -Unique)
    $difference = @(Compare-Object -ReferenceObject $expectedNormalized -DifferenceObject $actual)
    Assert-True ($difference.Count -eq 0) "$Label contains missing or unexpected properties"
}

function Assert-ExactStringSet([object[]] $Actual, [string[]] $Expected, [string] $Label) {
    $actualNormalized = @($Actual | ForEach-Object { [string] $_ } | Sort-Object -Unique)
    $expectedNormalized = @($Expected | Sort-Object -Unique)
    $difference = @(Compare-Object -ReferenceObject $expectedNormalized -DifferenceObject $actualNormalized)
    Assert-True ($difference.Count -eq 0) "$Label differs from the expected exact set"
}

function Assert-ExactIntSequence([object[]] $Actual, [int[]] $Expected, [string] $Label) {
    Assert-True ($Actual.Count -eq $Expected.Count) "$Label length differs from the expected sequence"
    for ($index = 0; $index -lt $Expected.Count; $index++) {
        Assert-True ([int] $Actual[$index] -eq $Expected[$index]) "$Label differs at index $index"
    }
}

function Read-Json([string] $Path, [string] $Label) {
    try {
        return Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json -Depth 64
    } catch {
        throw "$Label is not valid JSON: $($_.Exception.Message)"
    }
}

function Read-UniqueProperties([string] $Path, [string] $Label) {
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

function Assert-FileRecord(
    [object] $Record,
    [string] $ExpectedPath,
    [string] $Label
) {
    Assert-ExactObjectKeys $Record @('path', 'sizeBytes', 'sha256') $Label
    $recordPath = Resolve-ExistingFile ([string] (Get-RequiredMember $Record 'path' $Label)) "$Label path"
    if (-not [string]::IsNullOrWhiteSpace($ExpectedPath)) {
        $expectedFullPath = [IO.Path]::GetFullPath($ExpectedPath)
        Assert-True (
            $recordPath.Equals($expectedFullPath, [StringComparison]::OrdinalIgnoreCase)
        ) "$Label path differs from the expected file"
    }
    $actual = New-FileRecord $recordPath
    Assert-True ([long] (Get-RequiredMember $Record 'sizeBytes' $Label) -eq $actual.sizeBytes) "$Label size mismatch"
    $recordSha256 = Normalize-Sha256 ([string] (Get-RequiredMember $Record 'sha256' $Label)) "$Label SHA-256"
    Assert-True ($recordSha256 -ceq $actual.sha256) "$Label SHA-256 mismatch"
    return $actual
}

function Invoke-NativeCapture(
    [string] $FilePath,
    [string[]] $Arguments,
    [string] $Label
) {
    $lines = @(& $FilePath @Arguments 2>&1 | ForEach-Object { $_.ToString() })
    $exitCode = $LASTEXITCODE
    $text = [string]::Join([Environment]::NewLine, $lines)
    if ($exitCode -ne 0) {
        throw "$Label failed with exit code $exitCode`: $text"
    }
    return $text
}

function Get-ApkInfo([string] $Path, [string] $Role) {
    $badging = Invoke-NativeCapture $script:Aapt2 @('dump', 'badging', $Path) "$Role aapt2 inspection"
    $packageMatch = [regex]::Match(
        $badging,
        "(?m)^package:\s+name='([^']+)'\s+versionCode='([0-9]+)'\s+versionName='([^']*)'.*$"
    )
    Assert-True $packageMatch.Success "$Role has no parseable package/version badging"
    $sdkMatch = [regex]::Match($badging, "(?m)^(?:minSdkVersion|sdkVersion):'([^']+)'\s*$")
    $targetSdkMatch = [regex]::Match($badging, "(?m)^targetSdkVersion:'([^']+)'\s*$")
    $compileSdkMatch = [regex]::Match($packageMatch.Value, "compileSdkVersion='([^']+)'")
    Assert-True ($sdkMatch.Success -and $targetSdkMatch.Success -and $compileSdkMatch.Success) "$Role SDK badging is incomplete"
    $nativeMatch = [regex]::Match($badging, '(?m)^native-code:\s*(.+?)\s*$')
    Assert-True $nativeMatch.Success "$Role does not declare a native ABI"
    $abis = @(
        [regex]::Matches($nativeMatch.Groups[1].Value, "'([^']+)'") |
            ForEach-Object { $_.Groups[1].Value } |
            Sort-Object -Unique
    )
    Assert-True ($abis.Count -gt 0) "$Role native ABI list is empty"
    Assert-True ($badging -notmatch '(?m)^application-debuggable\s*$') "$Role is debuggable"

    $signing = Invoke-NativeCapture $script:ApkSigner @('verify', '--verbose', '--print-certs', $Path) "$Role apksigner verification"
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
    Assert-True ($signers.Count -eq 1) "$Role signer set is not an exact singleton"

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

function Assert-ApkIdentity(
    [System.Collections.IDictionary] $Info,
    [string] $ExpectedPackage,
    [long] $ExpectedVersionCode,
    [string] $ExpectedVersionName,
    [string[]] $ExpectedAbis,
    [string] $Label
) {
    Assert-True ($Info.packageName -ceq $ExpectedPackage) "$Label package name mismatch"
    Assert-True ($Info.versionCode -eq $ExpectedVersionCode) "$Label versionCode mismatch"
    Assert-True ($Info.versionName -ceq $ExpectedVersionName) "$Label versionName mismatch"
    Assert-ExactStringSet @($Info.abis) $ExpectedAbis "$Label ABI set"
    Assert-ExactStringSet @($Info.signerSha256) @($pinnedReleaseCertificateSha256) "$Label signer set"
    Assert-True ($Info.v2Verified -eq $true) "$Label v2 verification is false"
    Assert-True ($Info.debuggable -eq $false) "$Label is debuggable"
}

function Assert-ApkMatchesProvenance(
    [object] $Record,
    [System.Collections.IDictionary] $Info,
    [string] $ExpectedRole,
    [string] $Label
) {
    Assert-ExactObjectKeys $Record @(
        'role', 'file', 'packageName', 'versionCode', 'versionName', 'minSdk',
        'targetSdk', 'compileSdk', 'abis', 'signerSha256', 'v2Verified', 'debuggable'
    ) $Label
    Assert-True ([string] (Get-RequiredMember $Record 'role' $Label) -ceq $ExpectedRole) "$Label role mismatch"
    [void] (Assert-FileRecord (Get-RequiredMember $Record 'file' $Label) $Info.file.path "$Label file")
    foreach ($property in @('packageName', 'versionName', 'minSdk', 'targetSdk', 'compileSdk')) {
        Assert-True (
            [string] (Get-RequiredMember $Record $property $Label) -ceq [string] $Info[$property]
        ) "$Label $property mismatch"
    }
    Assert-True ([long] (Get-RequiredMember $Record 'versionCode' $Label) -eq $Info.versionCode) "$Label versionCode mismatch"
    Assert-ExactStringSet @((Get-RequiredMember $Record 'abis' $Label)) @($Info.abis) "$Label ABI record"
    Assert-ExactStringSet @((Get-RequiredMember $Record 'signerSha256' $Label)) @($Info.signerSha256) "$Label signer record"
    Assert-True ((Get-RequiredMember $Record 'v2Verified' $Label) -eq $true) "$Label provenance v2 flag is false"
    Assert-True ((Get-RequiredMember $Record 'debuggable' $Label) -eq $false) "$Label provenance debuggable flag is true"
}

function Assert-RepositoryRecord(
    [object] $Record,
    [string] $ExpectedCommit,
    [string] $Label
) {
    Assert-ExactObjectKeys $Record @('root', 'commit', 'commitCount', 'branch', 'clean') $Label
    $root = [IO.Path]::GetFullPath([string] (Get-RequiredMember $Record 'root' $Label))
    Assert-True (Test-Path -LiteralPath $root -PathType Container) "$Label root does not exist"
    $commit = ([string] (Get-RequiredMember $Record 'commit' $Label)).ToLowerInvariant()
    Assert-True ($commit -ceq $ExpectedCommit) "$Label commit mismatch"
    Assert-True ([long] (Get-RequiredMember $Record 'commitCount' $Label) -gt 0) "$Label commit count is invalid"
    Assert-True (-not [string]::IsNullOrWhiteSpace([string] (Get-RequiredMember $Record 'branch' $Label))) "$Label branch is empty"
    Assert-True ((Get-RequiredMember $Record 'clean' $Label) -eq $true) "$Label provenance is not clean"
}

function Assert-TestObservation([object] $Observation, [string] $ExpectedTest, [int] $Index) {
    $label = "P3 observation[$Index]"
    Assert-ExactObjectKeys $Observation @('test', 'result') $label
    Assert-True ([string] (Get-RequiredMember $Observation 'test' $label) -ceq $ExpectedTest) "$label test mismatch"
    Assert-True ([string] (Get-RequiredMember $Observation 'result' $label) -ceq 'OK_1_TEST_ZERO_SKIP') "$label result mismatch"
}

function Assert-PhaseObservation(
    [object] $Observation,
    [string] $ExpectedPhase,
    [long] $ExpectedVersionCode,
    [string] $ExpectedResult,
    [int] $Index
) {
    $label = "P3 observation[$Index]"
    Assert-ExactObjectKeys $Observation @('phase', 'versionCode', 'result') $label
    Assert-True ([string] (Get-RequiredMember $Observation 'phase' $label) -ceq $ExpectedPhase) "$label phase mismatch"
    Assert-True ([long] (Get-RequiredMember $Observation 'versionCode' $label) -eq $ExpectedVersionCode) "$label versionCode mismatch"
    Assert-True ([string] (Get-RequiredMember $Observation 'result' $label) -ceq $ExpectedResult) "$label result mismatch"
}

$ExpectedHostCommit = $ExpectedHostCommit.ToLowerInvariant()
$ExpectedPluginCommit = $ExpectedPluginCommit.ToLowerInvariant()
$ResolvedTagCommit = $ResolvedTagCommit.ToLowerInvariant()
$ProvenanceSha256 = Normalize-Sha256 $ProvenanceSha256 'Expected provenance SHA-256'
$P3EvidenceSha256 = Normalize-Sha256 $P3EvidenceSha256 'Expected P3 SHA-256'
$RemoteArm64Sha256 = Normalize-Sha256 $RemoteArm64Sha256 'Remote arm64-v8a SHA-256'
$RemoteX8664Sha256 = Normalize-Sha256 $RemoteX8664Sha256 'Remote x86_64 SHA-256'
$RemoteUniversalSha256 = Normalize-Sha256 $RemoteUniversalSha256 'Remote universal SHA-256'

Assert-True ($ExpectedHostCommit -ceq $pinnedHostCommit) 'Expected Host commit is not the frozen 6.8.0 Build 5275 integration commit'
Assert-True ($ResolvedTagCommit -ceq $ExpectedPluginCommit) 'Resolved tag commit differs from the frozen plugin commit'
Assert-True ($ReleaseTag -ceq $pinnedReleaseTag) 'Release tag is not v0.1.0'
Assert-True ($ReleaseUrl -ceq $pinnedReleaseUrl) 'Release URL is not the official stable GitHub Release URL'
Assert-True ($ReleaseId -gt 0) 'Release ID must be a positive GitHub Release ID'
Assert-True (-not $ReleaseDraft) 'Stable Release is still a draft'
Assert-True (-not $ReleasePrerelease) 'Stable Release is still marked prerelease'
Assert-True ($RemoteArm64SizeBytes -gt 0) 'Remote arm64-v8a asset size is invalid'
Assert-True ($RemoteX8664SizeBytes -gt 0) 'Remote x86_64 asset size is invalid'
Assert-True ($RemoteUniversalSizeBytes -gt 0) 'Remote universal asset size is invalid'
Assert-True ($ExpectedUserIds.Count -gt 0) 'Expected device user inventory is empty'
$normalizedUserIds = @($ExpectedUserIds | Sort-Object -Unique)
Assert-True ($normalizedUserIds.Count -eq $ExpectedUserIds.Count) 'Expected device user inventory contains duplicates'
Assert-True (@($normalizedUserIds | Where-Object { $_ -lt 0 }).Count -eq 0) 'Expected device user inventory contains a negative ID'

$publishedAt = [DateTimeOffset]::MinValue
Assert-True (
    [DateTimeOffset]::TryParseExact(
        $ReleasePublishedAtUtc,
        @('yyyy-MM-ddTHH:mm:ssZ', 'yyyy-MM-ddTHH:mm:ss.FFFFFFFZ'),
        [Globalization.CultureInfo]::InvariantCulture,
        [Globalization.DateTimeStyles]::AssumeUniversal -bor [Globalization.DateTimeStyles]::AdjustToUniversal,
        [ref] $publishedAt
    )
) 'Release published-at timestamp is not valid UTC'
Assert-True ($publishedAt -le [DateTimeOffset]::UtcNow.AddMinutes(5)) 'Release published-at timestamp is in the future'

$Provenance = Resolve-ExistingFile $Provenance 'Final provenance'
$P3Evidence = Resolve-ExistingFile $P3Evidence 'P3 evidence'
$LocalArm64Apk = Resolve-ExistingFile $LocalArm64Apk 'Local arm64-v8a APK'
$LocalX8664Apk = Resolve-ExistingFile $LocalX8664Apk 'Local x86_64 APK'
$LocalUniversalApk = Resolve-ExistingFile $LocalUniversalApk 'Local universal APK'
$DownloadedArm64Apk = Resolve-ExistingFile $DownloadedArm64Apk 'Downloaded arm64-v8a APK'
$DownloadedX8664Apk = Resolve-ExistingFile $DownloadedX8664Apk 'Downloaded x86_64 APK'
$DownloadedUniversalApk = Resolve-ExistingFile $DownloadedUniversalApk 'Downloaded universal APK'
$Aapt2 = Resolve-ExistingFile $Aapt2 'aapt2'
$ApkSigner = Resolve-ExistingFile $ApkSigner 'apksigner'
Assert-True ([IO.Path]::GetFileName($Aapt2) -ieq 'aapt2.exe') 'Aapt2 must identify aapt2.exe explicitly'
Assert-True ([IO.Path]::GetFileName($ApkSigner) -in @('apksigner.bat', 'apksigner.exe')) 'ApkSigner must identify apksigner.bat or apksigner.exe explicitly'

$reportsRoot = [IO.Path]::GetFullPath((Join-Path $pluginRepo 'build/reports'))
$reportsRootPrefix = $reportsRoot.TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
$outputPath = if ([IO.Path]::IsPathRooted($Output)) {
    [IO.Path]::GetFullPath($Output)
} else {
    [IO.Path]::GetFullPath((Join-Path $pluginRepo $Output))
}
Assert-True ($outputPath.StartsWith($reportsRootPrefix, [StringComparison]::OrdinalIgnoreCase)) 'Output must be a file below the ignored plugin build/reports directory'
Assert-True ([IO.Path]::GetExtension($outputPath) -ceq '.json') 'Output must use the .json extension'

Assert-True ((Get-Sha256 $Provenance) -ceq $ProvenanceSha256) 'Final provenance SHA-256 mismatch'
Assert-True ((Get-Sha256 $P3Evidence) -ceq $P3EvidenceSha256) 'P3 evidence SHA-256 mismatch'
$provenanceRecord = New-FileRecord $Provenance
$p3EvidenceRecord = New-FileRecord $P3Evidence
$provenanceJson = Read-Json $Provenance 'Final provenance'
$p3Json = Read-Json $P3Evidence 'P3 evidence'

Assert-ExactObjectKeys $provenanceJson @(
    'schemaVersion', 'createdAtUtc', 'claims', 'repositories', 'compatibility',
    'apks', 'buildInputs'
) 'Final provenance root'
Assert-True ([int] (Get-RequiredMember $provenanceJson 'schemaVersion' 'Final provenance') -eq 1) 'Final provenance schemaVersion is not 1'
$provenanceCreatedAt = [DateTimeOffset]::MinValue
Assert-True (
    [DateTimeOffset]::TryParse(
        [string] (Get-RequiredMember $provenanceJson 'createdAtUtc' 'Final provenance'),
        [Globalization.CultureInfo]::InvariantCulture,
        [Globalization.DateTimeStyles]::AssumeUniversal,
        [ref] $provenanceCreatedAt
    )
) 'Final provenance createdAtUtc is invalid'
Assert-True ($publishedAt -ge $provenanceCreatedAt.ToUniversalTime()) 'GitHub Release predates the final provenance'

$claims = Get-RequiredMember $provenanceJson 'claims' 'Final provenance'
Assert-ExactObjectKeys $claims @('evidenceLevel', 'published', 'deviceValidated', 'p3Validated') 'Final provenance claims'
Assert-True ([string] (Get-RequiredMember $claims 'evidenceLevel' 'Final provenance claims') -ceq 'RELEASE_CANDIDATE_LOCAL') 'Final provenance evidence level is not RELEASE_CANDIDATE_LOCAL'
Assert-True ((Get-RequiredMember $claims 'published' 'Final provenance claims') -eq $false) 'Final provenance already claims publication'
Assert-True ((Get-RequiredMember $claims 'deviceValidated' 'Final provenance claims') -eq $false) 'Final provenance already claims device validation'
Assert-True ((Get-RequiredMember $claims 'p3Validated' 'Final provenance claims') -eq $false) 'Final provenance already claims P3 validation'

$repositories = Get-RequiredMember $provenanceJson 'repositories' 'Final provenance'
Assert-ExactObjectKeys $repositories @('host', 'plugin') 'Final provenance repositories'
$hostRepository = Get-RequiredMember $repositories 'host' 'Final provenance repositories'
$pluginRepository = Get-RequiredMember $repositories 'plugin' 'Final provenance repositories'
Assert-RepositoryRecord $hostRepository $ExpectedHostCommit 'Host repository provenance'
Assert-RepositoryRecord $pluginRepository $ExpectedPluginCommit 'Plugin repository provenance'
Assert-True ([long] (Get-RequiredMember $pluginRepository 'commitCount' 'Plugin repository provenance') -eq $pinnedPluginVersionCode) 'Plugin commit count is not VERSION_BUILD 9'
Assert-True (
    [IO.Path]::GetFullPath([string] (Get-RequiredMember $pluginRepository 'root' 'Plugin repository provenance')).Equals(
        $pluginRepo,
        [StringComparison]::OrdinalIgnoreCase
    )
) 'Plugin provenance root differs from this verifier repository'

$compatibility = Get-RequiredMember $provenanceJson 'compatibility' 'Final provenance'
Assert-ExactObjectKeys $compatibility @('hostPackage', 'pluginPackage', 'protocolMin', 'protocolMax', 'declaredPluginAbis') 'Final provenance compatibility'
Assert-True ([string] (Get-RequiredMember $compatibility 'hostPackage' 'Final provenance compatibility') -ceq $pinnedHostPackage) 'Host package compatibility mismatch'
Assert-True ([string] (Get-RequiredMember $compatibility 'pluginPackage' 'Final provenance compatibility') -ceq $pinnedPluginPackage) 'Plugin package compatibility mismatch'
Assert-True ([string] (Get-RequiredMember $compatibility 'protocolMin' 'Final provenance compatibility') -ceq '1.0') 'Protocol minimum mismatch'
Assert-True ([string] (Get-RequiredMember $compatibility 'protocolMax' 'Final provenance compatibility') -ceq '1.1') 'Protocol maximum mismatch'
Assert-ExactStringSet @((Get-RequiredMember $compatibility 'declaredPluginAbis' 'Final provenance compatibility')) $declaredPluginAbis 'Declared plugin ABI set'

$buildInputs = Get-RequiredMember $provenanceJson 'buildInputs' 'Final provenance'
Assert-ExactObjectKeys $buildInputs @('releaseIdentity', 'hostApiDistribution', 'pythonRuntime', 'tools') 'Final provenance buildInputs'
$releaseIdentity = Get-RequiredMember $buildInputs 'releaseIdentity' 'Final provenance buildInputs'
Assert-ExactObjectKeys $releaseIdentity @('file', 'format', 'hostPackage', 'pluginPackage', 'keystoreSha256', 'certificateSha256') 'Release identity provenance'
$releaseIdentityFile = Assert-FileRecord (Get-RequiredMember $releaseIdentity 'file' 'Release identity provenance') '' 'Release identity lock'
Assert-True ([string] (Get-RequiredMember $releaseIdentity 'format' 'Release identity provenance') -ceq '1') 'Release identity format mismatch'
Assert-True ([string] (Get-RequiredMember $releaseIdentity 'hostPackage' 'Release identity provenance') -ceq $pinnedHostPackage) 'Release identity Host package mismatch'
Assert-True ([string] (Get-RequiredMember $releaseIdentity 'pluginPackage' 'Release identity provenance') -ceq $pinnedPluginPackage) 'Release identity plugin package mismatch'
Assert-True ([string] (Get-RequiredMember $releaseIdentity 'keystoreSha256' 'Release identity provenance') -ceq $pinnedReleaseKeystoreSha256) 'Release keystore SHA-256 pin mismatch'
Assert-True ([string] (Get-RequiredMember $releaseIdentity 'certificateSha256' 'Release identity provenance') -ceq $pinnedReleaseCertificateSha256) 'SM003 certificate SHA-256 pin mismatch'
$releaseIdentityProperties = Read-UniqueProperties $releaseIdentityFile.path 'Release identity lock'
$expectedReleaseIdentityProperties = [ordered]@{
    format = '1'
    'host.package' = $pinnedHostPackage
    'plugin.package' = $pinnedPluginPackage
    'release.keystore.sha256' = $pinnedReleaseKeystoreSha256
    'release.certificate.sha256' = $pinnedReleaseCertificateSha256
}
Assert-True ($releaseIdentityProperties.Count -eq $expectedReleaseIdentityProperties.Count) 'Release identity lock contains missing or unexpected keys'
foreach ($entry in $expectedReleaseIdentityProperties.GetEnumerator()) {
    Assert-True ($releaseIdentityProperties[$entry.Key] -ceq $entry.Value) "Release identity lock mismatch for $($entry.Key)"
}

$hostApiDistribution = Get-RequiredMember $buildInputs 'hostApiDistribution' 'Final provenance buildInputs'
Assert-ExactObjectKeys $hostApiDistribution @('file', 'hostCommit', 'sourceFingerprint', 'distributionManifestSha256', 'aars') 'Host API distribution provenance'
$hostApiLockFile = Assert-FileRecord (Get-RequiredMember $hostApiDistribution 'file' 'Host API distribution provenance') '' 'Host API AAR lock'
Assert-True ([string] (Get-RequiredMember $hostApiDistribution 'hostCommit' 'Host API distribution provenance') -ceq $ExpectedHostCommit) 'Host API distribution commit mismatch'
Assert-True ([string] (Get-RequiredMember $hostApiDistribution 'sourceFingerprint' 'Host API distribution provenance') -ceq $pinnedHostApiSourceFingerprint) 'Host API source fingerprint mismatch'
Assert-True ([string] (Get-RequiredMember $hostApiDistribution 'distributionManifestSha256' 'Host API distribution provenance') -ceq $pinnedHostApiDistributionManifestSha256) 'Host API distribution manifest SHA-256 mismatch'
$hostApiLockText = Get-Content -LiteralPath $hostApiLockFile.path -Raw -Encoding UTF8
$hostHeadMatch = [regex]::Match($hostApiLockText, '(?m)^# Host HEAD:\s*([0-9a-fA-F]{40,64})\s+\(clean current tree\)\s*$')
$sourceFingerprintMatch = [regex]::Match($hostApiLockText, '(?m)^# Host source fingerprint:\s*([0-9a-fA-F]{64})\s*$')
$manifestShaMatch = [regex]::Match($hostApiLockText, '(?m)^# Distribution manifest SHA-256:\s*([0-9a-fA-F]{64})\s*$')
Assert-True ($hostHeadMatch.Success -and $sourceFingerprintMatch.Success -and $manifestShaMatch.Success) 'Host API AAR lock provenance comments are incomplete'
Assert-True ($hostHeadMatch.Groups[1].Value.ToLowerInvariant() -ceq $ExpectedHostCommit) 'Host API AAR lock Host commit mismatch'
Assert-True ($sourceFingerprintMatch.Groups[1].Value.ToLowerInvariant() -ceq $pinnedHostApiSourceFingerprint) 'Host API AAR lock source fingerprint mismatch'
Assert-True ($manifestShaMatch.Groups[1].Value.ToLowerInvariant() -ceq $pinnedHostApiDistributionManifestSha256) 'Host API AAR lock distribution manifest mismatch'
$hostApiLockProperties = Read-UniqueProperties $hostApiLockFile.path 'Host API AAR lock'
$expectedHostApiLockKeys = @('format') + @(
    $hostApiDefinitions.Keys | ForEach-Object { @("$_.file", "$_.sha256") }
)
Assert-True ($hostApiLockProperties.Count -eq $expectedHostApiLockKeys.Count) 'Host API AAR lock inventory contains missing or unexpected properties'
Assert-True ($hostApiLockProperties['format'] -ceq '1') 'Host API AAR lock format is not 1'
Assert-ExactStringSet @($hostApiLockProperties.Keys) $expectedHostApiLockKeys 'Host API AAR lock key inventory'
$hostApiAars = Get-RequiredMember $hostApiDistribution 'aars' 'Host API distribution provenance'
Assert-ExactObjectKeys $hostApiAars @($hostApiDefinitions.Keys) 'Host API AAR provenance inventory'
$verifiedHostApiAars = [ordered]@{}
foreach ($id in $hostApiDefinitions.Keys) {
    $definition = $hostApiDefinitions[$id]
    Assert-True ($hostApiLockProperties["$id.file"] -ceq $definition.file) "$id lock filename mismatch"
    Assert-True ($hostApiLockProperties["$id.sha256"] -ceq $definition.sha256) "$id lock SHA-256 mismatch"
    $expectedAarPath = Join-Path (Join-Path $pluginRepo 'libs') $definition.file
    $record = Assert-FileRecord (Get-RequiredMember $hostApiAars $id 'Host API AAR provenance inventory') $expectedAarPath "$id AAR"
    Assert-True ($record.sha256 -ceq $definition.sha256) "$id AAR differs from the frozen Host 6.8.0 distribution"
    $verifiedHostApiAars[$id] = $record
}

$pythonRuntime = Get-RequiredMember $buildInputs 'pythonRuntime' 'Final provenance buildInputs'
Assert-ExactObjectKeys $pythonRuntime @('file', 'state', 'artifactCount', 'inventorySha256', 'pythonVersion', 'chaquopyVersion', 'abis', 'artifacts') 'Python runtime provenance'
[void] (Assert-FileRecord (Get-RequiredMember $pythonRuntime 'file' 'Python runtime provenance') '' 'Python runtime lock')
Assert-True ([string] (Get-RequiredMember $pythonRuntime 'state' 'Python runtime provenance') -ceq 'RESOLVED') 'Python runtime artifact inventory is not RESOLVED'
Assert-True ([long] (Get-RequiredMember $pythonRuntime 'artifactCount' 'Python runtime provenance') -gt 0) 'Python runtime artifact inventory is empty'
[void] (Normalize-Sha256 ([string] (Get-RequiredMember $pythonRuntime 'inventorySha256' 'Python runtime provenance')) 'Python runtime inventory SHA-256')
Assert-ExactStringSet @((Get-RequiredMember $pythonRuntime 'abis' 'Python runtime provenance')) $declaredPluginAbis 'Python runtime ABI set'

$apks = Get-RequiredMember $provenanceJson 'apks' 'Final provenance'
Assert-ExactObjectKeys $apks @('host', 'pluginArm64', 'pluginX8664', 'pluginUniversal', 'exactSignerSetSha256') 'Final provenance APK inventory'
$expectedSignerSetSha256 = Get-Utf8Sha256 ($pinnedReleaseCertificateSha256 + "`n")
Assert-True ([string] (Get-RequiredMember $apks 'exactSignerSetSha256' 'Final provenance APK inventory') -ceq $expectedSignerSetSha256) 'Final provenance signer-set SHA-256 mismatch'

$hostApkRecord = Get-RequiredMember $apks 'host' 'Final provenance APK inventory'
$hostApkFileRecord = Get-RequiredMember $hostApkRecord 'file' 'Host APK provenance'
$hostApkPath = Resolve-ExistingFile ([string] (Get-RequiredMember $hostApkFileRecord 'path' 'Host APK provenance file')) 'Host APK from provenance'
$hostApkInfo = Get-ApkInfo $hostApkPath 'host'
Assert-ApkIdentity $hostApkInfo $pinnedHostPackage $pinnedHostVersionCode $pinnedHostVersionName @($ExpectedDeviceAbi) 'Host APK'
Assert-ApkMatchesProvenance $hostApkRecord $hostApkInfo 'host' 'Host APK provenance'

$assetInputs = @(
    [ordered]@{
        architecture = 'arm64-v8a'; provenanceKey = 'pluginArm64'; role = 'plugin-arm64-v8a'
        localPath = $LocalArm64Apk; downloadedPath = $DownloadedArm64Apk
        localName = 'autojs6-plugin-python-runtime-v0.1.0-arm64-v8a.apk'
        remoteName = $RemoteArm64AssetName; remotePattern = '^autojs6-plugin-python-runtime-v0\.1\.0-arm64-v8a-[0-9a-f]{8}\.apk$'
        remoteSha256 = $RemoteArm64Sha256; remoteSizeBytes = $RemoteArm64SizeBytes
        expectedAbis = @('arm64-v8a')
    },
    [ordered]@{
        architecture = 'x86_64'; provenanceKey = 'pluginX8664'; role = 'plugin-x86_64'
        localPath = $LocalX8664Apk; downloadedPath = $DownloadedX8664Apk
        localName = 'autojs6-plugin-python-runtime-v0.1.0-x86_64.apk'
        remoteName = $RemoteX8664AssetName; remotePattern = '^autojs6-plugin-python-runtime-v0\.1\.0-x86_64-[0-9a-f]{8}\.apk$'
        remoteSha256 = $RemoteX8664Sha256; remoteSizeBytes = $RemoteX8664SizeBytes
        expectedAbis = @('x86_64')
    },
    [ordered]@{
        architecture = 'universal'; provenanceKey = 'pluginUniversal'; role = 'plugin-universal'
        localPath = $LocalUniversalApk; downloadedPath = $DownloadedUniversalApk
        localName = 'autojs6-plugin-python-runtime-v0.1.0-universal.apk'
        remoteName = $RemoteUniversalAssetName; remotePattern = '^autojs6-plugin-python-runtime-v0\.1\.0-universal-[0-9a-f]{8}\.apk$'
        remoteSha256 = $RemoteUniversalSha256; remoteSizeBytes = $RemoteUniversalSizeBytes
        expectedAbis = $declaredPluginAbis
    }
)
$verifiedReleaseAssets = @()
foreach ($asset in $assetInputs) {
    $label = "Plugin $($asset.architecture)"
    Assert-True ([IO.Path]::GetFileName($asset.localPath) -ceq $asset.localName) "$label local filename mismatch"
    Assert-True ($asset.remoteName -cmatch $asset.remotePattern) "$label remote asset name is not the digest-suffixed stable name"
    Assert-True ([IO.Path]::GetFileName($asset.downloadedPath) -ceq $asset.remoteName) "$label downloaded filename differs from the remote asset name"
    $localFile = New-FileRecord $asset.localPath
    $downloadedFile = New-FileRecord $asset.downloadedPath
    Assert-True ($localFile.sizeBytes -eq [long] $asset.remoteSizeBytes) "$label local size differs from remote metadata"
    Assert-True ($downloadedFile.sizeBytes -eq [long] $asset.remoteSizeBytes) "$label downloaded size differs from remote metadata"
    Assert-True ($localFile.sha256 -ceq $asset.remoteSha256) "$label local SHA-256 differs from remote metadata"
    Assert-True ($downloadedFile.sha256 -ceq $asset.remoteSha256) "$label downloaded SHA-256 differs from remote metadata"
    Assert-True ($localFile.sha256 -ceq $downloadedFile.sha256) "$label local and downloaded APK bytes differ"
    $localInfo = Get-ApkInfo $asset.localPath "$label local"
    $downloadedInfo = Get-ApkInfo $asset.downloadedPath "$label downloaded"
    Assert-ApkIdentity $localInfo $pinnedPluginPackage $pinnedPluginVersionCode $pinnedPluginVersionName $asset.expectedAbis "$label local APK"
    Assert-ApkIdentity $downloadedInfo $pinnedPluginPackage $pinnedPluginVersionCode $pinnedPluginVersionName $asset.expectedAbis "$label downloaded APK"
    $provenanceApk = Get-RequiredMember $apks $asset.provenanceKey 'Final provenance APK inventory'
    Assert-ApkMatchesProvenance $provenanceApk $localInfo $asset.role "$label provenance"
    $verifiedReleaseAssets += [ordered]@{
        architecture = $asset.architecture
        remote = [ordered]@{
            name = $asset.remoteName
            sizeBytes = [long] $asset.remoteSizeBytes
            sha256 = $asset.remoteSha256
        }
        local = $localFile
        downloaded = $downloadedFile
        packageName = $localInfo.packageName
        versionCode = $localInfo.versionCode
        versionName = $localInfo.versionName
        abis = @($localInfo.abis)
        signerSha256 = @($localInfo.signerSha256)
        v2Verified = $true
        debuggable = $false
    }
}

Assert-ExactObjectKeys $p3Json @(
    'schema', 'status', 'scope', 'exactSerial', 'expectedDevice', 'provenance',
    'candidateSignerSha256', 'differentSignerSha256', 'pluginVersions', 'observations',
    'packageRestoration', 'blockedRequirements', 'error', 'restorationErrors',
    'finalReceiptWritten', 'stableReleaseAuthorized'
) 'P3 evidence root'
Assert-True ([int] (Get-RequiredMember $p3Json 'schema' 'P3 evidence') -eq 1) 'P3 schema is not 1'
Assert-True ([string] (Get-RequiredMember $p3Json 'status' 'P3 evidence') -ceq 'PARTIAL_DIAGNOSTIC') 'P3 status is not PARTIAL_DIAGNOSTIC'
Assert-True ([string] (Get-RequiredMember $p3Json 'scope' 'P3 evidence') -ceq 'R6_RELEASE_CANDIDATE_CONCENTRATED_MATRIX_WITH_FRESH_DATA_ROLLBACK_NO_FINAL_RECEIPT') 'P3 scope mismatch'
Assert-True ([string] (Get-RequiredMember $p3Json 'exactSerial' 'P3 evidence') -ceq $ExpectedDeviceSerial) 'P3 device serial mismatch'
$p3Device = Get-RequiredMember $p3Json 'expectedDevice' 'P3 evidence'
Assert-ExactObjectKeys $p3Device @('api', 'abi', 'frozenUserIds') 'P3 expected device'
Assert-True ([int] (Get-RequiredMember $p3Device 'api' 'P3 expected device') -eq $ExpectedDeviceApi) 'P3 device API mismatch'
Assert-True ([string] (Get-RequiredMember $p3Device 'abi' 'P3 expected device') -ceq $ExpectedDeviceAbi) 'P3 device ABI mismatch'
$p3UserIds = @((Get-RequiredMember $p3Device 'frozenUserIds' 'P3 expected device') | ForEach-Object { [int] $_ })
Assert-ExactIntSequence $p3UserIds $normalizedUserIds 'P3 frozen user inventory'
$p3Provenance = Get-RequiredMember $p3Json 'provenance' 'P3 evidence'
Assert-ExactObjectKeys $p3Provenance @('path', 'sha256') 'P3 provenance binding'
Assert-True (
    [IO.Path]::GetFullPath([string] (Get-RequiredMember $p3Provenance 'path' 'P3 provenance binding')).Equals(
        $Provenance,
        [StringComparison]::OrdinalIgnoreCase
    )
) 'P3 provenance path differs from the final provenance input'
Assert-True ([string] (Get-RequiredMember $p3Provenance 'sha256' 'P3 provenance binding') -ceq $ProvenanceSha256) 'P3 provenance SHA-256 binding mismatch'
Assert-True ([string] (Get-RequiredMember $p3Json 'candidateSignerSha256' 'P3 evidence') -ceq $pinnedReleaseCertificateSha256) 'P3 candidate signer is not SM003'
Assert-True ([string] (Get-RequiredMember $p3Json 'differentSignerSha256' 'P3 evidence') -ceq $pinnedDifferentSignerSha256) 'P3 hostile signer mismatch'
$pluginVersions = Get-RequiredMember $p3Json 'pluginVersions' 'P3 evidence'
Assert-ExactObjectKeys $pluginVersions @('baseline', 'candidate') 'P3 plugin versions'
$baselineVersionCode = [long] (Get-RequiredMember $pluginVersions 'baseline' 'P3 plugin versions')
$candidateVersionCode = [long] (Get-RequiredMember $pluginVersions 'candidate' 'P3 plugin versions')
Assert-True ($baselineVersionCode -gt 0 -and $baselineVersionCode -lt $pinnedPluginVersionCode) 'P3 baseline versionCode is not an older positive build'
Assert-True ($candidateVersionCode -eq $pinnedPluginVersionCode) 'P3 candidate versionCode is not 9'

$observations = @((Get-RequiredMember $p3Json 'observations' 'P3 evidence'))
Assert-True ($observations.Count -eq 15) 'P3 must contain exactly 15 observations'
Assert-TestObservation $observations[0] $availabilityTest 0
Assert-PhaseObservation $observations[1] 'BASELINE_INSTALL' $baselineVersionCode 'AVAILABLE' 1
Assert-TestObservation $observations[2] $availabilityTest 2
Assert-PhaseObservation $observations[3] 'BASELINE_TO_CANDIDATE_UPGRADE' $pinnedPluginVersionCode 'AVAILABLE' 3
Assert-TestObservation $observations[4] $availabilityTest 4
Assert-TestObservation $observations[5] $availabilityTest 5
Assert-TestObservation $observations[6] $availabilityTest 6
Assert-TestObservation $observations[7] $availabilityTest 7
Assert-TestObservation $observations[8] $cancelRebindTest 8
Assert-TestObservation $observations[9] $timeoutRebindTest 9
Assert-TestObservation $observations[10] $sessionRelayTest 10
Assert-TestObservation $observations[11] $sameSignerTest 11
Assert-TestObservation $observations[12] $differentSignerTest 12
Assert-TestObservation $observations[13] $availabilityTest 13
Assert-PhaseObservation $observations[14] 'CANDIDATE_UNINSTALL_BASELINE_REINSTALL_ROLLBACK' $baselineVersionCode 'AVAILABLE_WITH_FRESH_APP_DATA' 14
Assert-True ([string] (Get-RequiredMember $p3Json 'packageRestoration' 'P3 evidence') -ceq 'VERIFIED_ABSENT_ALL_FROZEN_USERS_AND_GLOBAL') 'P3 package restoration was not verified'
Assert-ExactStringSet @((Get-RequiredMember $p3Json 'blockedRequirements' 'P3 evidence')) @(
    'INDEPENDENT_FINAL_RECEIPT_VERIFIER',
    'DECLARED_ABI_PACKAGING_AND_ACTUAL_DEVICE_COVERAGE_AGGREGATION'
) 'P3 blocked requirement set'
Assert-True ($null -eq (Get-RequiredMember $p3Json 'error' 'P3 evidence')) 'P3 contains a run error'
Assert-True (@((Get-RequiredMember $p3Json 'restorationErrors' 'P3 evidence')).Count -eq 0) 'P3 contains restoration errors'
Assert-True ((Get-RequiredMember $p3Json 'finalReceiptWritten' 'P3 evidence') -eq $false) 'P3 runner improperly wrote a final receipt'
Assert-True ((Get-RequiredMember $p3Json 'stableReleaseAuthorized' 'P3 evidence') -eq $false) 'P3 runner improperly authorized a stable release'

$receipt = [ordered]@{
    schemaVersion = 1
    createdAtUtc = [DateTimeOffset]::UtcNow.ToString('o')
    claims = [ordered]@{
        evidenceLevel = 'PRODUCTION_RELEASE'
        published = $true
        stableRelease = $true
        productionReleaseAuthorized = $true
    }
    release = [ordered]@{
        repository = 'SuperMonster003/AutoJs6-Plugin-Python-Runtime'
        tag = $ReleaseTag
        tagCommit = $ResolvedTagCommit
        id = $ReleaseId
        url = $ReleaseUrl
        publishedAtUtc = $publishedAt.ToUniversalTime().ToString('o')
        draft = $false
        prerelease = $false
        assets = @($verifiedReleaseAssets)
    }
    source = [ordered]@{
        hostCommit = $ExpectedHostCommit
        pluginCommit = $ExpectedPluginCommit
        hostVersionName = $pinnedHostVersionName
        hostVersionCode = $pinnedHostVersionCode
        pluginVersionName = $pinnedPluginVersionName
        pluginVersionCode = $pinnedPluginVersionCode
    }
    evidence = [ordered]@{
        finalProvenance = $provenanceRecord
        p3 = $p3EvidenceRecord
        p3ObservationCount = 15
        packageRestoration = 'VERIFIED_ABSENT_ALL_FROZEN_USERS_AND_GLOBAL'
    }
    identity = [ordered]@{
        hostPackage = $pinnedHostPackage
        pluginPackage = $pinnedPluginPackage
        signerSha256 = $pinnedReleaseCertificateSha256
        hostApk = $hostApkInfo.file
    }
    hostApiDistribution = [ordered]@{
        sourceFingerprint = $pinnedHostApiSourceFingerprint
        distributionManifestSha256 = $pinnedHostApiDistributionManifestSha256
        aars = $verifiedHostApiAars
    }
    deviceCoverage = [ordered]@{
        actualArm64 = [ordered]@{
            serial = $ExpectedDeviceSerial
            api = $ExpectedDeviceApi
            abi = $ExpectedDeviceAbi
            frozenUserIds = $normalizedUserIds
            observationCount = 15
            packageRestorationVerified = $true
            deviceValidated = $true
        }
        x86_64 = [ordered]@{
            status = 'PACKAGING_ONLY'
            declared = $true
            splitApkVerified = $true
            universalApkVerified = $true
            deviceValidated = $false
        }
    }
    boundaries = [ordered]@{
        runtimeTrustModel = 'TRUSTED_LOCAL_PYTHON_SCRIPTS_NON_SECURITY_SANDBOX'
        hostPublicReleaseVerified = $false
        x8664RuntimeDeviceEvidence = $false
        x8664Coverage = 'PACKAGING_ONLY'
    }
}

$outputDirectory = [IO.Path]::GetDirectoryName($outputPath)
[void] (New-Item -ItemType Directory -Path $outputDirectory -Force)
$temporaryPath = Join-Path $outputDirectory ('.' + [IO.Path]::GetFileName($outputPath) + '.' + [Guid]::NewGuid().ToString('N') + '.tmp')
$utf8WithoutBom = [Text.UTF8Encoding]::new($false)
try {
    $json = ($receipt | ConvertTo-Json -Depth 20) + "`n"
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
Write-Output 'R6_STABLE_RELEASE=PRODUCTION_RELEASE'
Write-Output 'PUBLISHED=true'
Write-Output 'STABLE_RELEASE=true'
Write-Output 'PRODUCTION_RELEASE_AUTHORIZED=true'
Write-Output "OUTPUT=$outputPath"
Write-Output "OUTPUT_SHA256=$outputSha256"
Write-Output "HOST_COMMIT=$ExpectedHostCommit"
Write-Output "PLUGIN_COMMIT=$ExpectedPluginCommit"
Write-Output "TAG_COMMIT=$ResolvedTagCommit"
