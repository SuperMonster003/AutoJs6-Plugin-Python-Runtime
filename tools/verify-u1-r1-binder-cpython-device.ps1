#Requires -Version 7.0

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $RawReport,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9A-Fa-f]{64}$')]
    [string] $RawReportSha256,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[A-Za-z0-9._:-]+$')]
    [string] $ExpectedSerial,

    [Parameter(Mandatory = $true)]
    [ValidateRange(1, 1000)]
    [int] $ExpectedApi,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[A-Za-z0-9_+.-]+$')]
    [string] $ExpectedAbi,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [int[]] $ExpectedUserIds,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $HostRepository,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $PluginRepository,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9A-Fa-f]{40,64}$')]
    [string] $ExpectedHostCommit,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9A-Fa-f]{40,64}$')]
    [string] $ExpectedPluginCommit,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $FunctionalGate,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9A-Fa-f]{64}$')]
    [string] $FunctionalGateSha256,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $ObservationFixture,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9A-Fa-f]{64}$')]
    [string] $ObservationFixtureSha256,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $HostApk,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9A-Fa-f]{64}$')]
    [string] $HostSha256,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $HostTestApk,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9A-Fa-f]{64}$')]
    [string] $HostTestSha256,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $PluginApk,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9A-Fa-f]{64}$')]
    [string] $PluginSha256,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9A-Fa-f: ]{64,128}$')]
    [string] $ExpectedSignerSha256,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $AdbPath,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $Aapt2Path,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $ApkSignerPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false

$hostPackage = 'org.autojs.autojs6'
$hostTestPackage = 'org.autojs.autojs6.test'
$pluginPackage = 'io.github.supermonster003.autojs6.plugin.python.runtime'
$rawScope = 'U1_R1_BINDER_CPYTHON_EXACT_DEVICE_CELL'
$evidenceLevel = 'BINDER_CPYTHON_DEVICE_PARTIAL'
$maximumInstrumentationOutputBytes = 1MB
$sha256Pattern = '^[0-9a-f]{64}$'
$reservedInstrumentationArguments = @(
    'class', 'notClass', 'package', 'notPackage', 'annotation', 'notAnnotation',
    'size', 'numShards', 'shardIndex', 'log', 'debug', 'coverage'
)
$expectedObservationDefinitions = @(
    [pscustomobject][ordered]@{
        id = 'public-semantics'
        selector = 'org.autojs.autojs.engine.PythonU1R1AcceptanceInstrumentationTest#publicScriptEngineRunsStdinStdlibRelativeImportsAndIsolatesSequentialWorkspaces'
        arguments = [ordered]@{
            'autojs.python.u1r1.acceptance.enabled' = 'true'
        }
        covered = @(
            'REAL_CPYTHON_3_13_9',
            'PUBLIC_ENGINE_STDIN_SNAPSHOT',
            'INPUT_PROMPT_AND_UNICODE_LINES',
            'PACKAGED_STDLIB_IMPORTS',
            'PROJECT_AND_RELATIVE_IMPORTS',
            'SEQUENTIAL_WORKSPACE_ISOLATION',
            'PINNED_PROVIDER_CALLBACK_UID',
            'ONE_STARTED_ONE_TERMINAL'
        )
    },
    [pscustomobject][ordered]@{
        id = 'start-lease'
        selector = 'org.autojs.autojs.core.plugin.python.PythonRuntimeU1R1StartLeaseInstrumentationTest#openedButNeverStartedSessionExpiresAndNextExecutionSucceeds'
        arguments = [ordered]@{
            'autojs.python.u1r1.startLease.enabled' = 'true'
        }
        covered = @(
            'OPENED_SESSION_START_LEASE',
            'NO_USER_CODE_BEFORE_START',
            'LEASE_RELEASES_SLOT_AND_DESCRIPTORS',
            'NEXT_FINITE_EXECUTION_SUCCEEDS'
        )
    }
)
$expectedLimitations = @(
    'SINGLE_DEVICE_API_ABI_CELL',
    'NO_X86_64_DEVICE_EXECUTION',
    'NO_DEVICE_MATRIX',
    'NO_PUBLIC_RELEASE_VERIFICATION',
    'NO_LIVE_INTERACTIVE_STDIN',
    'TRUSTED_LOCAL_CODE_NOT_SANDBOX'
)
$git = (Get-Command git -CommandType Application -ErrorAction Stop).Source
$utf8WithoutBom = [Text.UTF8Encoding]::new($false)

function Assert-True([bool] $Condition, [string] $Message) {
    if (-not $Condition) { throw $Message }
}

function Normalize-Sha256([string] $Value, [string] $Label) {
    $normalized = ($Value -replace '[^0-9A-Fa-f]', '').ToLowerInvariant()
    Assert-True ($normalized -match $sha256Pattern) "$Label is not one exact SHA-256 digest"
    return $normalized
}

function Normalize-Commit([string] $Value, [string] $Label) {
    $normalized = $Value.Trim().ToLowerInvariant()
    Assert-True ($normalized -match '^[0-9a-f]{40,64}$') "$Label is not a full Git commit"
    return $normalized
}

function Resolve-ExistingFile([string] $Path, [string] $Label) {
    $fullPath = [IO.Path]::GetFullPath($Path)
    Assert-True (Test-Path -LiteralPath $fullPath -PathType Leaf) "$Label is not an existing file"
    Assert-True ((Get-Item -LiteralPath $fullPath).Length -gt 0) "$Label is empty"
    return $fullPath
}

function Resolve-ExistingDirectory([string] $Path, [string] $Label) {
    $fullPath = [IO.Path]::GetFullPath($Path)
    Assert-True (Test-Path -LiteralPath $fullPath -PathType Container) "$Label is not an existing directory"
    return $fullPath.TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
}

function Get-FileSha256([string] $Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Get-TextSha256([string] $Text) {
    $algorithm = [Security.Cryptography.SHA256]::Create()
    try {
        return [Convert]::ToHexString($algorithm.ComputeHash($utf8WithoutBom.GetBytes($Text))).ToLowerInvariant()
    } finally {
        $algorithm.Dispose()
    }
}

function Invoke-NativeCapture([string] $Executable, [string[]] $Arguments, [string] $Label) {
    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $lines = @(& $Executable @Arguments 2>&1 | ForEach-Object { $_.ToString() })
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
    $text = [string]::Join("`n", $lines)
    if ($exitCode -ne 0) {
        throw "$Label failed with exit code $exitCode`n$text"
    }
    return [pscustomobject]@{ Text = $text; Lines = $lines; ExitCode = [int] $exitCode }
}

function Assert-NativeSuccess([object] $Result, [string] $Label) {
    Assert-True ($null -ne $Result -and [int] $Result.ExitCode -eq 0) "$Label did not complete successfully"
}

function Invoke-Git([string] $Repository, [string[]] $Arguments, [string] $Label) {
    return (Invoke-NativeCapture $git (@('-C', $Repository) + $Arguments) $Label).Text.Trim()
}

function Read-Json([string] $Path, [string] $Label) {
    try {
        return Get-Content -Raw -LiteralPath $Path -Encoding UTF8 | ConvertFrom-Json -Depth 100
    } catch {
        throw "$Label is not valid JSON: $($_.Exception.Message)"
    }
}

function Assert-ExactKeys([object] $Object, [string[]] $Expected, [string] $Label) {
    Assert-True ($null -ne $Object) "$Label is null"
    $actual = @($Object.PSObject.Properties | ForEach-Object { $_.Name } | Sort-Object)
    $wanted = @($Expected | Sort-Object)
    Assert-True ($actual.Count -eq $wanted.Count) "$Label key count differs; expected=$($wanted -join ',') actual=$($actual -join ',')"
    for ($index = 0; $index -lt $wanted.Count; $index++) {
        Assert-True ($actual[$index] -ceq $wanted[$index]) "$Label keys differ; expected=$($wanted -join ',') actual=$($actual -join ',')"
    }
}

function Get-RequiredMember([object] $Object, [string] $Name, [string] $Label) {
    Assert-True ($null -ne $Object) "$Label is null"
    $property = $Object.PSObject.Properties[$Name]
    Assert-True ($null -ne $property) "$Label is missing $Name"
    return $property.Value
}

function Assert-StringSequence([object[]] $Actual, [string[]] $Expected, [string] $Label) {
    Assert-True ($Actual.Count -eq $Expected.Count) "$Label length differs"
    for ($index = 0; $index -lt $Expected.Count; $index++) {
        Assert-True ([string] $Actual[$index] -ceq $Expected[$index]) "$Label differs at index $index"
    }
}

function Assert-IntSequence([object[]] $Actual, [int[]] $Expected, [string] $Label) {
    Assert-True ($Actual.Count -eq $Expected.Count) "$Label length differs"
    for ($index = 0; $index -lt $Expected.Count; $index++) {
        Assert-True ([int] $Actual[$index] -eq $Expected[$index]) "$Label differs at index $index"
    }
}

function Assert-DateTime([object] $Value, [string] $Label) {
    $parsed = [DateTimeOffset]::MinValue
    Assert-True ([DateTimeOffset]::TryParse([string] $Value, [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::RoundtripKind, [ref] $parsed)) "$Label is not an ISO-8601 timestamp"
    return $parsed
}

function Get-RepositoryIdentity([string] $Repository, [string] $ExpectedCommit, [string] $Label) {
    $root = Resolve-ExistingDirectory $Repository $Label
    $topLevel = Invoke-Git $root @('rev-parse', '--show-toplevel') "$Label Git root inspection"
    Assert-True ([IO.Path]::GetFullPath($topLevel).Equals($root, [StringComparison]::OrdinalIgnoreCase)) "$Label path is not its Git top-level directory"
    $head = (Invoke-Git $root @('rev-parse', '--verify', 'HEAD') "$Label HEAD inspection").ToLowerInvariant()
    Assert-True ($head -ceq $ExpectedCommit) "$Label HEAD differs from the expected commit"
    $status = Invoke-Git $root @('status', '--porcelain=v1', '--untracked-files=all') "$Label clean-tree inspection"
    Assert-True ($status.Length -eq 0) "$Label worktree is not clean"
    $branch = Invoke-Git $root @('rev-parse', '--abbrev-ref', 'HEAD') "$Label branch inspection"
    return [pscustomobject][ordered]@{ repository = $root; commit = $head; branch = $branch; clean = $true }
}

function Assert-RepositoryRecord([object] $Record, [object] $Live, [string] $Label) {
    Assert-ExactKeys $Record @('repository', 'commit', 'branch', 'clean') $Label
    Assert-True ([IO.Path]::GetFullPath([string] $Record.repository).Equals($Live.repository, [StringComparison]::OrdinalIgnoreCase)) "$Label repository path differs"
    Assert-True ([string] $Record.commit -ceq $Live.commit) "$Label commit differs"
    Assert-True ([string] $Record.branch -ceq $Live.branch) "$Label branch differs"
    Assert-True ($Record.clean -eq $true) "$Label is not recorded clean"
}

function Assert-FunctionalGate([object] $Gate, [string] $ExpectedHost, [string] $ExpectedPlugin) {
    Assert-ExactKeys $Gate @(
        'schema', 'track', 'phase', 'status', 'reportRole', 'startedAtUtc', 'completedAtUtc',
        'evidenceLevels', 'sourceIdentity', 'scope', 'localPython', 'steps', 'claims', 'error'
    ) 'U1-R1 functional gate root'
    Assert-True ([int] $Gate.schema -eq 1 -and [string] $Gate.track -ceq 'U1' -and [string] $Gate.phase -ceq 'R1') 'Functional gate identity differs'
    Assert-True ([string] $Gate.status -ceq 'PASS' -and [string] $Gate.reportRole -ceq 'CURRENT_TREE_FUNCTIONAL_GATE') 'Functional gate did not produce the expected PASS role'
    Assert-StringSequence @($Gate.evidenceLevels) @('PORTABLE_CPYTHON_ONLY', 'ANDROID_BUILD_ONLY') 'Functional gate evidence levels'
    Assert-ExactKeys $Gate.sourceIdentity @('plugin', 'host') 'Functional gate source identity'
    foreach ($definition in @(
        [pscustomobject]@{ Name = 'host'; Commit = $ExpectedHost },
        [pscustomobject]@{ Name = 'plugin'; Commit = $ExpectedPlugin }
    )) {
        $identity = Get-RequiredMember $Gate.sourceIdentity $definition.Name 'Functional gate source identity'
        Assert-ExactKeys $identity @('repository', 'commit', 'dirty', 'changes') "Functional gate $($definition.Name) identity"
        Assert-True ([string] $identity.commit -ceq $definition.Commit -and $identity.dirty -eq $false -and @($identity.changes).Count -eq 0) "Functional gate $($definition.Name) identity differs"
    }
    Assert-ExactKeys $Gate.claims @(
        'portableTestsPassed', 'androidCompiled', 'apkPackaged', 'hostChecked',
        'binderExecuted', 'deviceVerified', 'productionEvidence', 'published', 'releaseAuthorized'
    ) 'Functional gate claims'
    foreach ($name in @('portableTestsPassed', 'androidCompiled', 'apkPackaged', 'hostChecked')) {
        Assert-True ((Get-RequiredMember $Gate.claims $name 'Functional gate claims') -eq $true) "Functional gate claim $name is not true"
    }
    foreach ($name in @('binderExecuted', 'deviceVerified', 'productionEvidence', 'published', 'releaseAuthorized')) {
        Assert-True ((Get-RequiredMember $Gate.claims $name 'Functional gate claims') -eq $false) "Functional gate claim $name exceeds E2"
    }
    Assert-True ($null -eq $Gate.error) 'Functional gate contains an error'
}

function Assert-ArgumentObject([object] $Arguments, [string] $Label) {
    Assert-True ($null -ne $Arguments) "$Label is null"
    foreach ($property in $Arguments.PSObject.Properties) {
        Assert-True ($property.Name -match '^[A-Za-z0-9._-]+$') "$Label contains an unsafe argument name"
        Assert-True ($property.Name -cnotin $reservedInstrumentationArguments) "$Label contains reserved instrumentation argument $($property.Name)"
        Assert-True ($property.Value -is [string] -and -not [string]::IsNullOrWhiteSpace([string] $property.Value)) "$Label contains a non-string or blank value"
    }
}

function Assert-ObservationFixture([object] $Fixture) {
    Assert-ExactKeys $Fixture @('schemaVersion', 'contract', 'track', 'phase', 'runnerComponent', 'instrumentationArguments', 'selectors') 'Observation fixture root'
    Assert-True ([int] $Fixture.schemaVersion -eq 1) 'Observation fixture schema differs'
    Assert-True ([string] $Fixture.contract -ceq 'AUTOJS6_PYTHON_RUNTIME_U1_R1_DEVICE_OBSERVATIONS') 'Observation fixture contract differs'
    Assert-True ([string] $Fixture.track -ceq 'U1' -and [string] $Fixture.phase -ceq 'R1') 'Observation fixture track/phase differs'
    Assert-True ([string] $Fixture.runnerComponent -ceq "$hostTestPackage/androidx.test.runner.AndroidJUnitRunner") 'Observation fixture runner component differs'
    Assert-ArgumentObject $Fixture.instrumentationArguments 'Observation fixture global arguments'
    Assert-ExactKeys $Fixture.instrumentationArguments @() 'Observation fixture global arguments'
    $selectors = @($Fixture.selectors)
    Assert-True ($selectors.Count -eq $expectedObservationDefinitions.Count) 'Observation fixture selector count differs from the frozen U1-R1 contract'
    $ids = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    $names = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    for ($index = 0; $index -lt $selectors.Count; $index++) {
        $item = $selectors[$index]
        $expectedDefinition = $expectedObservationDefinitions[$index]
        Assert-ExactKeys $item @('id', 'selector', 'arguments', 'covered') 'Observation fixture selector'
        Assert-True ([string] $item.id -match '^[a-z][a-z0-9-]*$' -and $ids.Add([string] $item.id)) 'Observation fixture selector ID is unsafe or duplicated'
        Assert-True ([string] $item.selector -match '^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+#[A-Za-z_][A-Za-z0-9_]*$' -and $names.Add([string] $item.selector)) 'Observation fixture selector is malformed or duplicated'
        Assert-ArgumentObject $item.arguments "Observation fixture arguments for $($item.id)"
        foreach ($property in $item.arguments.PSObject.Properties) {
            Assert-True ($null -eq $Fixture.instrumentationArguments.PSObject.Properties[$property.Name]) "Selector $($item.id) overrides a global argument"
        }
        $covered = @($item.covered)
        Assert-True ($covered.Count -gt 0 -and @($covered | Sort-Object -Unique).Count -eq $covered.Count) "Selector $($item.id) coverage is empty or duplicated"
        foreach ($label in $covered) { Assert-True ([string] $label -match '^[A-Z][A-Z0-9_]*$') "Selector $($item.id) coverage label is unsafe" }
        Assert-True ([string] $item.id -ceq [string] $expectedDefinition.id) "Observation fixture selector ID differs at index $index"
        Assert-True ([string] $item.selector -ceq [string] $expectedDefinition.selector) "Observation fixture selector differs at index $index"
        Assert-ExactKeys $item.arguments @($expectedDefinition.arguments.Keys) "Observation fixture selector arguments at index $index"
        foreach ($entry in $expectedDefinition.arguments.GetEnumerator()) {
            Assert-True ([string] $item.arguments.PSObject.Properties[$entry.Key].Value -ceq [string] $entry.Value) "Observation fixture selector argument $($entry.Key) differs at index $index"
        }
        Assert-StringSequence @($item.covered) @($expectedDefinition.covered) "Observation fixture coverage at index $index"
    }
}

function Get-ApkSigner([string] $Path) {
    $result = Invoke-NativeCapture $script:resolvedApkSigner @('verify', '--verbose', '--print-certs', $Path) "apksigner verification for $Path"
    Assert-True ($result.Text -match '(?im)^Verified using v2 scheme \(APK Signature Scheme v2\):\s*true\s*$') "APK v2 verification did not pass for $Path"
    $matches = [regex]::Matches($result.Text, '(?im)^\s*(?:V\d+\s+)?Signer(?:\s+#?\d+)?\s*:?\s+certificate\s+SHA-256\s+digest:\s*([0-9a-fA-F: ]+)\s*$')
    $digests = @($matches | ForEach-Object { Normalize-Sha256 $_.Groups[1].Value "APK signer for $Path" } | Sort-Object -Unique)
    Assert-True ($digests.Count -eq 1) "APK signer set is not an exact singleton for $Path"
    return $digests[0]
}

function Inspect-Apk([string] $Role, [string] $Path, [string] $ExpectedSha, [string] $ExpectedPackage, [bool] $RequireExactAbi) {
    $resolved = Resolve-ExistingFile $Path "$Role APK"
    $sha = Get-FileSha256 $resolved
    Assert-True ($sha -ceq $ExpectedSha) "$Role APK SHA-256 mismatch"
    $result = Invoke-NativeCapture $script:resolvedAapt2 @('dump', 'badging', $resolved) "aapt2 inspection for $Role"
    $match = [regex]::Match($result.Text, "(?m)^package:\s+name='([^']+)'\s+versionCode='([0-9]*)'\s+versionName='([^']*)'")
    Assert-True $match.Success "Unable to parse $Role APK package/version"
    Assert-True ($match.Groups[1].Value -ceq $ExpectedPackage) "$Role APK package differs"
    $versionCodeText = $match.Groups[2].Value
    $versionCode = $null
    if ([string]::IsNullOrEmpty($versionCodeText)) {
        Assert-True ($Role -ceq 'androidTest') "$Role APK versionCode is unexpectedly empty"
    } else {
        $parsedVersionCode = 0L
        Assert-True ([long]::TryParse($versionCodeText, [ref] $parsedVersionCode) -and $parsedVersionCode -ge 0L) "$Role APK versionCode is invalid"
        $versionCode = $parsedVersionCode
    }
    $nativeMatch = [regex]::Match($result.Text, '(?m)^native-code:\s*(.*)$')
    $abis = if ($nativeMatch.Success) { @([regex]::Matches($nativeMatch.Groups[1].Value, "'([^']+)'") | ForEach-Object { $_.Groups[1].Value }) } else { @() }
    if ($RequireExactAbi) { Assert-StringSequence $abis @($ExpectedAbi) "$Role APK native ABI set" }
    $signer = Get-ApkSigner $resolved
    Assert-True ($signer -ceq $script:expectedSigner) "$Role APK signer differs"
    return [pscustomobject][ordered]@{
        role = $Role
        path = $resolved
        sizeBytes = [long] (Get-Item -LiteralPath $resolved).Length
        sha256 = $sha
        packageName = $ExpectedPackage
        versionCode = $versionCode
        versionName = $match.Groups[3].Value
        nativeAbis = $abis
        signerSha256 = $signer
        v2Verified = $true
        debuggable = [bool] ($result.Text -match '(?m)^application-debuggable(?:\s|$)')
    }
}

function Assert-ArtifactRecord([object] $Record, [object] $Live, [string] $Label) {
    Assert-ExactKeys $Record @('role', 'path', 'sizeBytes', 'sha256', 'packageName', 'versionCode', 'versionName', 'nativeAbis', 'signerSha256', 'v2Verified', 'debuggable') $Label
    Assert-True ([IO.Path]::GetFullPath([string] $Record.path).Equals($Live.path, [StringComparison]::OrdinalIgnoreCase)) "$Label path differs"
    foreach ($name in @('role', 'sizeBytes', 'sha256', 'packageName', 'versionCode', 'versionName', 'signerSha256', 'v2Verified', 'debuggable')) {
        Assert-True ((Get-RequiredMember $Record $name $Label) -ceq (Get-RequiredMember $Live $name $Label)) "$Label differs for $name"
    }
    # ConvertFrom-Json materializes an APK with no native-code line as null,
    # while the live aapt2 inspection retains an empty Object[] value. Both
    # represent the same exact empty ABI set; do not admit a non-null element.
    [object[]] $recordNativeAbis = @()
    if ($null -ne $Record.nativeAbis) { $recordNativeAbis = @($Record.nativeAbis) }
    [string[]] $liveNativeAbis = @()
    if ($null -ne $Live.nativeAbis) { $liveNativeAbis = @($Live.nativeAbis) }
    Assert-StringSequence $recordNativeAbis $liveNativeAbis "$Label native ABI set"
}

function Assert-FileBinding([object] $Record, [string] $Path, [string] $Sha, [string] $Label, [string[]] $ExtraKeys) {
    Assert-ExactKeys $Record (@('path', 'sizeBytes', 'sha256') + $ExtraKeys) $Label
    Assert-True ([IO.Path]::GetFullPath([string] $Record.path).Equals($Path, [StringComparison]::OrdinalIgnoreCase)) "$Label path differs"
    Assert-True ([long] $Record.sizeBytes -eq (Get-Item -LiteralPath $Path).Length) "$Label size differs"
    Assert-True ([string] $Record.sha256 -ceq $Sha) "$Label SHA-256 differs"
}

function Assert-AbsentPackageState([object] $State, [string] $PackageName, [int[]] $Users, [string] $Label) {
    Assert-ExactKeys $State @('packageName', 'globalRecordCount', 'userStates') $Label
    Assert-True ([string] $State.packageName -ceq $PackageName -and [int] $State.globalRecordCount -eq 0) "$Label package/global record differs"
    $states = @($State.userStates)
    Assert-True ($states.Count -eq $Users.Count) "$Label user-state count differs"
    for ($index = 0; $index -lt $Users.Count; $index++) {
        $user = $states[$index]
        Assert-ExactKeys $user @('userId', 'listed', 'paths') "$Label user state"
        Assert-True ([int] $user.userId -eq $Users[$index] -and $user.listed -eq $false -and @($user.paths).Count -eq 0) "$Label is not absent for user $($Users[$index])"
    }
}

function Assert-Claims([object] $Claims) {
    $expected = [ordered]@{
        portableTestsPassed = $true
        androidCompiled = $true
        apkPackaged = $true
        binderExecuted = $true
        packagedCpythonExecuted = $true
        deviceVerified = $true
        stdinVerified = $true
        importsVerified = $true
        sequentialIsolationVerified = $true
        restorationVerified = $true
        deviceMatrixVerified = $false
        productionEvidence = $false
        published = $false
        releaseAuthorized = $false
    }
    Assert-ExactKeys $Claims @($expected.Keys) 'Raw device claims'
    foreach ($entry in $expected.GetEnumerator()) {
        Assert-True ((Get-RequiredMember $Claims $entry.Key 'Raw device claims') -eq $entry.Value) "Raw device claim $($entry.Key) differs"
    }
}

function New-ExpectedMergedArguments([object] $Definition) {
    $merged = [ordered]@{}
    foreach ($property in @($Definition.arguments.PSObject.Properties | Sort-Object Name)) {
        Assert-True (-not $merged.Contains($property.Name)) "Duplicate expected instrumentation argument $($property.Name)"
        $merged[$property.Name] = [string] $property.Value
    }
    return [pscustomobject] $merged
}

function Split-InstrumentationSelector([string] $Selector) {
    $separator = $Selector.LastIndexOf('#')
    Assert-True ($separator -gt 0 -and $separator -lt $Selector.Length - 1) 'Instrumentation selector is not an exact class#method pair'
    return [pscustomobject]@{
        ClassName = $Selector.Substring(0, $separator)
        TestName = $Selector.Substring($separator + 1)
    }
}

function Assert-Observation([object] $Record, [object] $Definition, [int] $Index) {
    $label = "Raw observation $Index"
    Assert-ExactKeys $Record @(
        'id', 'selector', 'arguments', 'observedClass', 'observedTest',
        'observedClassRecordCount', 'observedTestRecordCount', 'covered',
        'startedAtUtc', 'completedAtUtc', 'elapsedMillis',
        'exitCode', 'output', 'outputUtf8Bytes', 'outputSha256', 'outputLineCount',
        'lastNonBlankLine', 'okCount', 'startStatusCount', 'terminalStatusCount',
        'successCodeCount', 'result'
    ) $label
    Assert-True ([string] $Record.id -ceq [string] $Definition.id -and [string] $Record.selector -ceq [string] $Definition.selector) "$label identity differs"
    $expectedArguments = New-ExpectedMergedArguments $Definition
    Assert-ExactKeys $Record.arguments @($expectedArguments.PSObject.Properties | ForEach-Object { $_.Name }) "$label arguments"
    foreach ($property in $expectedArguments.PSObject.Properties) {
        Assert-True ([string] $Record.arguments.PSObject.Properties[$property.Name].Value -ceq [string] $property.Value) "$label argument $($property.Name) differs"
    }
    $expectedIdentity = Split-InstrumentationSelector ([string] $Definition.selector)
    Assert-StringSequence @($Record.covered) @($Definition.covered) "$label coverage"
    $started = Assert-DateTime $Record.startedAtUtc "$label start time"
    $completed = Assert-DateTime $Record.completedAtUtc "$label completion time"
    Assert-True ($completed -ge $started -and [long] $Record.elapsedMillis -ge 0) "$label timing is invalid"
    Assert-True ([int] $Record.exitCode -eq 0) "$label native exit code is nonzero"
    $output = [string] $Record.output
    $byteCount = [long] $utf8WithoutBom.GetByteCount($output)
    Assert-True ($byteCount -le $maximumInstrumentationOutputBytes -and [long] $Record.outputUtf8Bytes -eq $byteCount) "$label output byte count differs"
    Assert-True ([string] $Record.outputSha256 -ceq (Get-TextSha256 $output)) "$label output SHA-256 differs"
    [string[]] $lines = @()
    if ($output.Length -gt 0) { $lines = @($output -split "`n") }
    Assert-True ([int] $Record.outputLineCount -eq $lines.Count) "$label output line count differs"
    $last = @($lines | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Select-Object -Last 1)
    $expectedLast = if ($last.Count -eq 1) { [string] $last[0] } else { '' }
    Assert-True ([string] $Record.lastNonBlankLine -ceq $expectedLast) "$label last output line differs"
    $okCount = [regex]::Matches($output, '(?m)^\s*OK \(1 test\)\s*$').Count
    $numTests = @([regex]::Matches($output, '(?m)^INSTRUMENTATION_STATUS:\s*numtests=(\d+)\s*$') | ForEach-Object { [int] $_.Groups[1].Value })
    $observedClasses = @([regex]::Matches($output, '(?m)^INSTRUMENTATION_STATUS:\s*class=([^\r\n]+)\s*$') | ForEach-Object { $_.Groups[1].Value.Trim() })
    $observedTests = @([regex]::Matches($output, '(?m)^INSTRUMENTATION_STATUS:\s*test=([^\r\n]+)\s*$') | ForEach-Object { $_.Groups[1].Value.Trim() })
    $observedClassSet = @($observedClasses | Sort-Object -Unique)
    $observedTestSet = @($observedTests | Sort-Object -Unique)
    $startCount = [regex]::Matches($output, '(?m)^INSTRUMENTATION_STATUS_CODE:\s*1\s*$').Count
    $terminalCount = [regex]::Matches($output, '(?m)^INSTRUMENTATION_STATUS_CODE:\s*0\s*$').Count
    $successCodeCount = [regex]::Matches($output, '(?m)^INSTRUMENTATION_CODE:\s*-1\s*$').Count
    $hasSkip = $output -match 'INSTRUMENTATION_STATUS_CODE:\s*-3(?:\s|$)|AssumptionViolatedException|(?im)^INSTRUMENTATION_STATUS:\s+(?:ignored|skipped)=|(?im)\b(?:ignored|skipped)\s*[:=]\s*[1-9][0-9]*\b'
    $hasFailure = $output -match '(?m)^(?:FAILURES!!!|INSTRUMENTATION_FAILED:)' -or $output -match '(?m)^INSTRUMENTATION_STATUS_CODE:\s*-[124-9][0-9]*\s*$'
    Assert-True ($okCount -eq 1 -and [int] $Record.okCount -eq 1) "$label does not contain exactly one OK (1 test)"
    Assert-True ($numTests.Count -gt 0 -and @($numTests | Where-Object { $_ -ne 1 }).Count -eq 0) "$label numtests evidence differs"
    Assert-True ($observedClasses.Count -ge 2 -and $observedClassSet.Count -eq 1 -and $observedClassSet[0] -ceq $expectedIdentity.ClassName) "$label observed class does not prove the fixture class"
    Assert-True ($observedTests.Count -ge 2 -and $observedTestSet.Count -eq 1 -and $observedTestSet[0] -ceq $expectedIdentity.TestName) "$label observed test does not prove the fixture method"
    Assert-True ([string] $Record.observedClass -ceq $expectedIdentity.ClassName -and [int] $Record.observedClassRecordCount -eq $observedClasses.Count) "$label recorded observed class differs"
    Assert-True ([string] $Record.observedTest -ceq $expectedIdentity.TestName -and [int] $Record.observedTestRecordCount -eq $observedTests.Count) "$label recorded observed test differs"
    Assert-True ($startCount -eq 1 -and [int] $Record.startStatusCount -eq 1) "$label does not contain exactly one start status"
    Assert-True ($terminalCount -eq 1 -and [int] $Record.terminalStatusCount -eq 1) "$label terminal status differs"
    Assert-True ($successCodeCount -eq 1 -and [int] $Record.successCodeCount -eq 1) "$label does not contain exactly one success code"
    Assert-True (-not $hasSkip -and -not $hasFailure) "$label contains skip/failure evidence"
    Assert-True ([string] $Record.result -ceq 'OK_1_TEST_ZERO_SKIP') "$label result differs"
}

function Write-NewCanonicalJson([string] $Path, [object] $Value) {
    $directory = [IO.Path]::GetDirectoryName($Path)
    [void] [IO.Directory]::CreateDirectory($directory)
    Assert-True (-not (Test-Path -LiteralPath $Path)) 'Canonical U1-R1 device evidence already exists and will not be overwritten'
    $temporary = Join-Path $directory ('.' + [IO.Path]::GetFileName($Path) + '.' + [Guid]::NewGuid().ToString('N') + '.tmp')
    try {
        [IO.File]::WriteAllText($temporary, (($Value | ConvertTo-Json -Depth 30) + "`n"), $utf8WithoutBom)
        Assert-True (-not (Test-Path -LiteralPath $Path)) 'Canonical U1-R1 device evidence appeared concurrently and will not be overwritten'
        [IO.File]::Move($temporary, $Path)
    } finally {
        if (Test-Path -LiteralPath $temporary -PathType Leaf) { Remove-Item -LiteralPath $temporary -Force }
    }
}

$expectedHost = Normalize-Commit $ExpectedHostCommit 'Expected Host commit'
$expectedPlugin = Normalize-Commit $ExpectedPluginCommit 'Expected Plugin commit'
$expectedUsers = @($ExpectedUserIds | Sort-Object)
Assert-True ($expectedUsers.Count -eq $ExpectedUserIds.Count -and @($expectedUsers | Sort-Object -Unique).Count -eq $expectedUsers.Count) 'ExpectedUserIds contains duplicates'
Assert-True (@($expectedUsers | Where-Object { $_ -lt 0 }).Count -eq 0 -and 0 -in $expectedUsers) 'ExpectedUserIds must contain unique non-negative IDs including user 0'
$script:expectedSigner = Normalize-Sha256 $ExpectedSignerSha256 'Expected signer SHA-256'
$hostIdentity = Get-RepositoryIdentity $HostRepository $expectedHost 'Host repository'
$pluginIdentity = Get-RepositoryIdentity $PluginRepository $expectedPlugin 'Plugin repository'
$scriptRepository = [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot)).TrimEnd('\', '/')
Assert-True ($pluginIdentity.repository.Equals($scriptRepository, [StringComparison]::OrdinalIgnoreCase)) 'PluginRepository differs from the repository containing this verifier'

$rawPath = Resolve-ExistingFile $RawReport 'Raw U1-R1 device report'
$rawDigest = Normalize-Sha256 $RawReportSha256 'Raw report SHA-256'
Assert-True ((Get-FileSha256 $rawPath) -ceq $rawDigest) 'Raw report SHA-256 mismatch'
$functionalPath = Resolve-ExistingFile $FunctionalGate 'U1-R1 functional gate'
$functionalDigest = Normalize-Sha256 $FunctionalGateSha256 'Functional gate SHA-256'
Assert-True ((Get-FileSha256 $functionalPath) -ceq $functionalDigest) 'Functional gate SHA-256 mismatch'
$functionalJson = Read-Json $functionalPath 'U1-R1 functional gate'
Assert-FunctionalGate $functionalJson $expectedHost $expectedPlugin
$fixturePath = Resolve-ExistingFile $ObservationFixture 'U1-R1 observation fixture'
$fixtureDigest = Normalize-Sha256 $ObservationFixtureSha256 'Observation fixture SHA-256'
$canonicalFixturePath = [IO.Path]::GetFullPath((Join-Path $pluginIdentity.repository 'tools/tests/fixtures/u1-r1-device-observation-contract.json'))
Assert-True ($fixturePath.Equals($canonicalFixturePath, [StringComparison]::OrdinalIgnoreCase)) 'Observation fixture must be the canonical tracked U1-R1 contract'
Assert-True ((Get-FileSha256 $fixturePath) -ceq $fixtureDigest) 'Observation fixture SHA-256 mismatch'
$fixture = Read-Json $fixturePath 'U1-R1 observation fixture'
Assert-ObservationFixture $fixture

$script:resolvedAapt2 = Resolve-ExistingFile $Aapt2Path 'aapt2'
$script:resolvedApkSigner = Resolve-ExistingFile $ApkSignerPath 'apksigner'
$resolvedAdb = Resolve-ExistingFile $AdbPath 'adb'
Assert-True ([IO.Path]::GetFileName($resolvedAdb) -in @('adb.exe', 'adb')) 'AdbPath must identify adb explicitly'
Assert-True ([IO.Path]::GetFileName($script:resolvedAapt2) -in @('aapt2.exe', 'aapt2')) 'Aapt2Path must identify aapt2 explicitly'
Assert-True ([IO.Path]::GetFileName($script:resolvedApkSigner) -in @('apksigner.bat', 'apksigner.exe', 'apksigner')) 'ApkSignerPath must identify apksigner explicitly'

$hostInfo = Inspect-Apk 'host' $HostApk (Normalize-Sha256 $HostSha256 'Host APK SHA-256') $hostPackage $true
$testInfo = Inspect-Apk 'androidTest' $HostTestApk (Normalize-Sha256 $HostTestSha256 'Host test APK SHA-256') $hostTestPackage $false
$pluginInfo = Inspect-Apk 'plugin' $PluginApk (Normalize-Sha256 $PluginSha256 'Plugin APK SHA-256') $pluginPackage $true
$raw = Read-Json $rawPath 'Raw U1-R1 device report'
Assert-ExactKeys $raw @(
    'schemaVersion', 'createdAtUtc', 'status', 'scope', 'evidenceLevel', 'source',
    'functionalGate', 'observationContract', 'artifacts', 'tools', 'device', 'preflight',
    'observations', 'restoration', 'claims', 'limitations', 'error'
) 'Raw U1-R1 device report root'
Assert-True ([int] $raw.schemaVersion -eq 1) 'Raw report schema differs'
$null = Assert-DateTime $raw.createdAtUtc 'Raw report creation time'
Assert-True ([string] $raw.status -ceq 'PASS' -and [string] $raw.scope -ceq $rawScope -and [string] $raw.evidenceLevel -ceq $evidenceLevel) 'Raw report status/scope/evidence level differs'
Assert-True ($null -eq $raw.error) 'Raw report contains an error'

Assert-ExactKeys $raw.source @('host', 'plugin') 'Raw source binding'
Assert-RepositoryRecord $raw.source.host $hostIdentity 'Raw Host source binding'
Assert-RepositoryRecord $raw.source.plugin $pluginIdentity 'Raw Plugin source binding'
Assert-FileBinding $raw.functionalGate $functionalPath $functionalDigest 'Raw functional gate binding' @('status', 'reportRole')
Assert-True ([string] $raw.functionalGate.status -ceq 'PASS' -and [string] $raw.functionalGate.reportRole -ceq 'CURRENT_TREE_FUNCTIONAL_GATE') 'Raw functional gate claim differs'
Assert-FileBinding $raw.observationContract $fixturePath $fixtureDigest 'Raw observation contract binding' @('schemaVersion')
Assert-True ([int] $raw.observationContract.schemaVersion -eq 1) 'Raw observation contract schema differs'

Assert-ExactKeys $raw.artifacts @('host', 'androidTest', 'plugin') 'Raw artifact set'
Assert-ArtifactRecord $raw.artifacts.host $hostInfo 'Raw Host artifact'
Assert-ArtifactRecord $raw.artifacts.androidTest $testInfo 'Raw Host test artifact'
Assert-ArtifactRecord $raw.artifacts.plugin $pluginInfo 'Raw Plugin artifact'

Assert-ExactKeys $raw.tools @('adb', 'aapt2', 'apkSigner') 'Raw tool set'
foreach ($definition in @(
    [pscustomobject]@{ Name = 'adb'; Path = $resolvedAdb; InvokeVersion = $false },
    [pscustomobject]@{ Name = 'aapt2'; Path = $script:resolvedAapt2; InvokeVersion = $true },
    [pscustomobject]@{ Name = 'apkSigner'; Path = $script:resolvedApkSigner; InvokeVersion = $true }
)) {
    $record = Get-RequiredMember $raw.tools $definition.Name 'Raw tool set'
    Assert-FileBinding $record $definition.Path (Get-FileSha256 $definition.Path) "Raw $($definition.Name) tool" @('versionOutputSha256')
    Assert-True ([string] $record.versionOutputSha256 -match $sha256Pattern) "Raw $($definition.Name) version output digest is invalid"
    if ($definition.InvokeVersion) {
        $version = Invoke-NativeCapture $definition.Path @('version') "$($definition.Name) version inspection"
        Assert-True ([string] $record.versionOutputSha256 -ceq (Get-TextSha256 $version.Text)) "Raw $($definition.Name) version output digest differs"
    }
}

Assert-ExactKeys $raw.device @('serial', 'api', 'abi', 'abiList', 'fingerprint', 'frozenUserIds') 'Raw device cell'
Assert-True ([string] $raw.device.serial -ceq $ExpectedSerial -and [int] $raw.device.api -eq $ExpectedApi -and [string] $raw.device.abi -ceq $ExpectedAbi) 'Raw exact device cell differs'
Assert-True (-not [string]::IsNullOrWhiteSpace([string] $raw.device.fingerprint)) 'Raw device fingerprint is blank'
Assert-True ($ExpectedAbi -in @($raw.device.abiList)) 'Raw device ABI list omits the expected ABI'
Assert-IntSequence @($raw.device.frozenUserIds) $expectedUsers 'Raw frozen user inventory'

Assert-ExactKeys $raw.preflight @(
    'confirmNoActiveSoak', 'confirmDeviceMutation', 'mutexName', 'deviceState',
    'userInventory', 'initialPackageStates', 'relevantProcesses'
) 'Raw preflight'
Assert-True ($raw.preflight.confirmNoActiveSoak -eq $true) 'Raw preflight lacks the current-run no-active-soak confirmation'
Assert-True ($raw.preflight.confirmDeviceMutation -eq $true) 'Raw preflight lacks the current-run mutation confirmation'
$expectedMutexName = 'Global\AutoJs6-Codex-Device-' + ([regex]::Replace($ExpectedSerial, '[^A-Za-z0-9_.-]', '_'))
Assert-True ([string] $raw.preflight.mutexName -ceq $expectedMutexName) 'Raw preflight device mutex name differs'
Assert-True ([string] $raw.preflight.deviceState -ceq 'device') 'Raw preflight device state differs'
Assert-IntSequence @($raw.preflight.userInventory) $expectedUsers 'Raw preflight user inventory'
Assert-True (@($raw.preflight.relevantProcesses).Count -eq 0) 'Raw preflight has relevant processes'
Assert-ExactKeys $raw.preflight.initialPackageStates @('host', 'androidTest', 'plugin') 'Raw initial package states'
Assert-AbsentPackageState $raw.preflight.initialPackageStates.host $hostPackage $expectedUsers 'Raw initial Host state'
Assert-AbsentPackageState $raw.preflight.initialPackageStates.androidTest $hostTestPackage $expectedUsers 'Raw initial Host test state'
Assert-AbsentPackageState $raw.preflight.initialPackageStates.plugin $pluginPackage $expectedUsers 'Raw initial Plugin state'

$rawObservations = @($raw.observations)
$definitions = @($fixture.selectors)
Assert-True ($rawObservations.Count -eq $definitions.Count) 'Raw observation count differs from the fixture'
for ($index = 0; $index -lt $definitions.Count; $index++) {
    Assert-Observation $rawObservations[$index] $definitions[$index] $index
}

Assert-ExactKeys $raw.restoration @(
    'verified', 'userInventoryUnchanged', 'packagesRestored', 'processesClean',
    'temporaryInstalls', 'finalPackageStates', 'finalRelevantProcesses', 'errors'
) 'Raw restoration'
foreach ($name in @('verified', 'userInventoryUnchanged', 'packagesRestored', 'processesClean')) {
    Assert-True ((Get-RequiredMember $raw.restoration $name 'Raw restoration') -eq $true) "Raw restoration claim $name is not true"
}
Assert-True (@($raw.restoration.errors).Count -eq 0 -and @($raw.restoration.finalRelevantProcesses).Count -eq 0) 'Raw restoration contains errors or relevant processes'
Assert-ExactKeys $raw.restoration.finalPackageStates @('host', 'androidTest', 'plugin') 'Raw final package states'
Assert-AbsentPackageState $raw.restoration.finalPackageStates.host $hostPackage $expectedUsers 'Raw final Host state'
Assert-AbsentPackageState $raw.restoration.finalPackageStates.androidTest $hostTestPackage $expectedUsers 'Raw final Host test state'
Assert-AbsentPackageState $raw.restoration.finalPackageStates.plugin $pluginPackage $expectedUsers 'Raw final Plugin state'
$installs = @($raw.restoration.temporaryInstalls)
$expectedInstallRoles = @('host', 'plugin', 'androidTest')
$expectedInstallPackages = @($hostPackage, $pluginPackage, $hostTestPackage)
Assert-True ($installs.Count -eq $expectedInstallRoles.Count) 'Raw temporary install count differs'
for ($index = 0; $index -lt $installs.Count; $index++) {
    $install = $installs[$index]
    Assert-ExactKeys $install @('role', 'packageName', 'installAttempted', 'installedByRun', 'installedPullVerified', 'removedByRun') "Raw temporary install $index"
    Assert-True ([string] $install.role -ceq $expectedInstallRoles[$index] -and [string] $install.packageName -ceq $expectedInstallPackages[$index]) "Raw temporary install $index identity differs"
    foreach ($name in @('installAttempted', 'installedByRun', 'installedPullVerified', 'removedByRun')) {
        Assert-True ((Get-RequiredMember $install $name "Raw temporary install $index") -eq $true) "Raw temporary install $index claim $name is not true"
    }
}

Assert-Claims $raw.claims
Assert-StringSequence @($raw.limitations) $expectedLimitations 'Raw evidence limitations'

# Recheck mutable local inputs immediately before publishing the canonical development report.
$null = Get-RepositoryIdentity $hostIdentity.repository $expectedHost 'Final Host repository'
$null = Get-RepositoryIdentity $pluginIdentity.repository $expectedPlugin 'Final Plugin repository'
Assert-True ((Get-FileSha256 $rawPath) -ceq $rawDigest) 'Raw report changed during verification'
Assert-True ((Get-FileSha256 $functionalPath) -ceq $functionalDigest) 'Functional gate changed during verification'
Assert-True ((Get-FileSha256 $fixturePath) -ceq $fixtureDigest) 'Observation fixture changed during verification'
foreach ($info in @($hostInfo, $testInfo, $pluginInfo)) {
    Assert-True ((Get-FileSha256 $info.path) -ceq $info.sha256) "$($info.role) APK changed during verification"
}

$canonicalPath = [IO.Path]::GetFullPath((Join-Path $pluginIdentity.repository 'build/reports/python/u1/r1-binder-cpython-device.json'))
$canonicalRelative = $canonicalPath.Substring($pluginIdentity.repository.Length).TrimStart('\', '/').Replace('\', '/')
$ignored = Invoke-NativeCapture $git @('-C', $pluginIdentity.repository, 'check-ignore', '--quiet', '--no-index', '--', $canonicalRelative) 'canonical output ignore-policy inspection'
Assert-NativeSuccess $ignored 'Canonical output ignore-policy inspection'
$canonical = [pscustomobject][ordered]@{
    schemaVersion = 1
    createdAtUtc = [DateTimeOffset]::UtcNow.ToString('o')
    status = 'PASS'
    scope = $rawScope
    evidenceLevel = $evidenceLevel
    rawEvidence = [pscustomobject][ordered]@{
        path = $rawPath
        sizeBytes = [long] (Get-Item -LiteralPath $rawPath).Length
        sha256 = $rawDigest
    }
    source = $raw.source
    functionalGate = $raw.functionalGate
    observationContract = $raw.observationContract
    artifacts = $raw.artifacts
    device = $raw.device
    preflight = $raw.preflight
    observations = $raw.observations
    restoration = $raw.restoration
    claims = $raw.claims
    limitations = $raw.limitations
    boundaries = [pscustomobject][ordered]@{
        matrix = $false
        release = $false
        published = $false
        releaseAuthorized = $false
    }
}
Write-NewCanonicalJson $canonicalPath $canonical
$canonicalSha = Get-FileSha256 $canonicalPath
Write-Output 'U1_R1_DEVICE_EVIDENCE=BINDER_CPYTHON_DEVICE_PARTIAL'
Write-Output "OUTPUT=$canonicalPath"
Write-Output "OUTPUT_SHA256=$canonicalSha"
Write-Output 'MATRIX_VERIFIED=false'
Write-Output 'PUBLISHED=false'
Write-Output 'RELEASE_AUTHORIZED=false'
