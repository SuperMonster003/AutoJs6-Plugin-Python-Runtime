#Requires -Version 7.0

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[A-Za-z0-9._:-]+$')]
    [string] $Serial,

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
    [string] $ApkSignerPath,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $Output,

    [Parameter(Mandatory = $true)]
    [switch] $ConfirmNoActiveSoak,

    [Parameter(Mandatory = $true)]
    [switch] $ConfirmDeviceMutation,

    [ValidateSet('U1-R1', 'U1-R2')]
    [string] $EvidenceProfile = 'U1-R1'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false

$hostPackage = 'org.autojs.autojs6'
$hostTestPackage = 'org.autojs.autojs6.test'
$pluginPackage = 'io.github.supermonster003.autojs6.plugin.python.runtime'
$isR2Profile = $EvidenceProfile -ceq 'U1-R2'
$phase = if ($isR2Profile) { 'R2' } else { 'R1' }
$profileLabel = "U1-$phase"
$rawScope = if ($isR2Profile) { 'U1_R2_BINDER_CPYTHON_EXACT_DEVICE_CELL' } else { 'U1_R1_BINDER_CPYTHON_EXACT_DEVICE_CELL' }
$evidenceLevel = 'BINDER_CPYTHON_DEVICE_PARTIAL'
$fixtureContract = if ($isR2Profile) { 'AUTOJS6_PYTHON_RUNTIME_U1_R2_DEVICE_OBSERVATIONS' } else { 'AUTOJS6_PYTHON_RUNTIME_U1_R1_DEVICE_OBSERVATIONS' }
$fixtureRelativePath = if ($isR2Profile) { 'tools/tests/fixtures/u1-r2-device-observation-contract.json' } else { 'tools/tests/fixtures/u1-r1-device-observation-contract.json' }
$rawOutputPrefix = if ($isR2Profile) { 'r2-binder-cpython-device-run-' } else { 'r1-binder-cpython-device-run-' }
$functionalGateRole = if ($isR2Profile) { 'CURRENT_TREE_R2_E3_FUNCTIONAL_GATE' } else { 'CURRENT_TREE_FUNCTIONAL_GATE' }
$functionalGateEvidenceLevels = if ($isR2Profile) {
    @('PORTABLE_CPYTHON_ONLY', 'ANDROID_BUILD_ONLY', 'HOST_ANDROID_TEST_BUILD_ONLY')
} else {
    @('PORTABLE_CPYTHON_ONLY', 'ANDROID_BUILD_ONLY')
}
$maximumInstrumentationOutputBytes = 1MB
$sha256Pattern = '^[0-9a-f]{64}$'
$reservedInstrumentationArguments = @(
    'class', 'notClass', 'package', 'notPackage', 'annotation', 'notAnnotation',
    'size', 'numShards', 'shardIndex', 'log', 'debug', 'coverage'
)
$r1ObservationDefinitions = @(
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
$r2ObservationDefinitions = @(
    [pscustomobject][ordered]@{
        id = 'public-module-result-artifact'
        selector = 'org.autojs.autojs.engine.PythonU1R2AcceptanceInstrumentationTest#publicModuleEngineReturnsExplicitJsonAndExactArtifactWithoutInferringStdout'
        arguments = [ordered]@{ 'autojs.python.u1r2.public.enabled' = 'true' }
        covered = @(
            'REAL_CPYTHON_3_13_9',
            'PUBLIC_ENGINE_MODULE_ENTRY',
            'MODULE_RUNPY_METADATA_AND_RELATIVE_IMPORT',
            'EXPLICIT_STRUCTURED_JSON_RESULT',
            'OUTPUT_ARTIFACT_EXACT_LENGTH_EOF_SHA256_BYTES',
            'HOST_OWNED_DEFENSIVE_ARTIFACT_BYTES',
            'STDOUT_RESULT_INFERENCE_FORBIDDEN',
            'ONE_STARTED_ONE_TERMINAL'
        )
    },
    [pscustomobject][ordered]@{
        id = 'binder-interactive-stream'
        selector = 'org.autojs.autojs.core.plugin.python.PythonRuntimeU1R2BinderInstrumentationTest#interactivePromptReplyStreamsBeforeTerminalAndKeepsStdoutOutOfResult'
        arguments = [ordered]@{ 'autojs.python.u1r2.binder.enabled' = 'true' }
        covered = @(
            'EXACT_COMPONENT_BIND',
            'PINNED_PROVIDER_CALLBACK_UID',
            'EXECUTION_TIME_ORDERED_STDOUT_BEFORE_PROMPT',
            'TYPED_PROMPT_ID_POLICY',
            'ONE_SHOT_BOUNDED_UTF8_REPLY',
            'STDOUT_RESULT_INFERENCE_FORBIDDEN',
            'ONE_STARTED_ONE_TERMINAL'
        )
    },
    [pscustomobject][ordered]@{
        id = 'binder-artifact-limit-recovery'
        selector = 'org.autojs.autojs.core.plugin.python.PythonRuntimeU1R2BinderInstrumentationTest#oversizedArtifactPublishesNoPartialResultThenNextExactBindSucceeds'
        arguments = [ordered]@{ 'autojs.python.u1r2.binder.enabled' = 'true' }
        covered = @(
            'RESULT_POLICY_PER_ARTIFACT_LIMIT',
            'OUTPUT_ARTIFACT_REJECTED_RESULT_PHASE',
            'NO_PARTIAL_RESULT_OR_DESCRIPTORS',
            'NEXT_EXACT_BIND_SUCCEEDS',
            'PINNED_PROVIDER_CALLBACK_UID',
            'ONE_STARTED_ONE_TERMINAL'
        )
    },
    [pscustomobject][ordered]@{
        id = 'cancel-rebind'
        selector = 'org.autojs.autojs.core.plugin.python.PythonRuntimeRealPluginCancelRebindDiagnosticTest#cancelAfterStartedKillsOldBinderThenExactRebindRunsFiniteRequestOnce'
        arguments = [ordered]@{ 'autojs.python.r2.cancelRebind.enabled' = 'true' }
        covered = @(
            'CANCEL_AFTER_STARTED',
            'TYPED_CANCELLATION',
            'OLD_PROVIDER_BINDER_DEATH',
            'NO_DISPATCH_REPLAY',
            'EXACT_REBIND_NEW_RUNTIME_GENERATION',
            'NEXT_FINITE_EXECUTION_SUCCEEDS',
            'PINNED_PROVIDER_CALLBACK_UID'
        )
    },
    [pscustomobject][ordered]@{
        id = 'timeout-rebind'
        selector = 'org.autojs.autojs.core.plugin.python.PythonRuntimeRealPluginTimeoutRebindDiagnosticTest#providerTimeoutFailsBeforeOldBinderDeathThenExactRebindRunsFiniteRequest'
        arguments = [ordered]@{ 'autojs.python.r2.timeoutRebind.enabled' = 'true' }
        covered = @(
            'PROVIDER_EXECUTION_TIMEOUT',
            'TYPED_TIMEOUT_BEFORE_BINDER_DEATH',
            'NO_HOST_CANCEL',
            'NO_DISPATCH_REPLAY',
            'EXACT_REBIND_NEW_RUNTIME_GENERATION',
            'NEXT_FINITE_EXECUTION_SUCCEEDS',
            'PINNED_PROVIDER_CALLBACK_UID'
        )
    }
)
$expectedObservationDefinitions = if ($isR2Profile) { $r2ObservationDefinitions } else { $r1ObservationDefinitions }
$limitations = @(
    'SINGLE_DEVICE_API_ABI_CELL',
    'NO_X86_64_DEVICE_EXECUTION',
    'NO_DEVICE_MATRIX',
    'NO_PUBLIC_RELEASE_VERIFICATION',
    $(if ($isR2Profile) { 'NO_FOREGROUND_UI_AUTOMATION' } else { 'NO_LIVE_INTERACTIVE_STDIN' }),
    'TRUSTED_LOCAL_CODE_NOT_SANDBOX'
)
$git = (Get-Command git -CommandType Application -ErrorAction Stop).Source
$utf8WithoutBom = [Text.UTF8Encoding]::new($false)

function Assert-True([bool] $Condition, [string] $Message) {
    if (-not $Condition) {
        throw $Message
    }
}

function Normalize-Sha256([string] $Value, [string] $Label) {
    $normalized = ($Value -replace '[^0-9A-Fa-f]', '').ToLowerInvariant()
    Assert-True ($normalized -match $sha256Pattern) "$Label is not one exact SHA-256 digest"
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

function Get-Utf8ByteCount([string] $Text) {
    return [long] $utf8WithoutBom.GetByteCount($Text)
}

function Invoke-NativeCapture {
    param(
        [Parameter(Mandatory = $true)] [string] $Executable,
        [Parameter(Mandatory = $true)] [string[]] $Arguments,
        [Parameter(Mandatory = $true)] [string] $Label
    )
    $started = [DateTimeOffset]::UtcNow
    $stopwatch = [Diagnostics.Stopwatch]::StartNew()
    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $lines = @(& $Executable @Arguments 2>&1 | ForEach-Object { $_.ToString() })
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousErrorActionPreference
        $stopwatch.Stop()
    }
    $text = [string]::Join("`n", $lines)
    return [pscustomobject]@{
        Label = $Label
        Arguments = $Arguments
        ExitCode = [int] $exitCode
        Lines = $lines
        Text = $text
        StartedAtUtc = $started.ToString('o')
        CompletedAtUtc = [DateTimeOffset]::UtcNow.ToString('o')
        ElapsedMillis = [long] $stopwatch.ElapsedMilliseconds
    }
}

function Assert-NoCompetingDeviceOrGradleClient {
    $gradleClients = @(
        Get-CimInstance Win32_Process -Filter "Name = 'java.exe'" -ErrorAction Stop |
            Where-Object { [string] $_.CommandLine -match '(?i)gradle-wrapper\.jar' }
    )
    Assert-True ($gradleClients.Count -eq 0) 'An active Gradle wrapper client prevents exact-device evidence collection'
    $adbClients = @(
        Get-CimInstance Win32_Process -Filter "Name = 'adb.exe'" -ErrorAction Stop |
            Where-Object {
                $commandLine = [string] $_.CommandLine
                -not [string]::IsNullOrWhiteSpace($commandLine) -and
                    $commandLine -notmatch '(?i)\bfork-server\s+server\b'
            }
    )
    Assert-True ($adbClients.Count -eq 0) 'A non-server adb.exe client prevents exact-device evidence collection'
}

function Assert-NativeSuccess([pscustomobject] $Result) {
    if ($Result.ExitCode -ne 0) {
        $detail = if ($Result.Text.Length -gt 0) { "`n$($Result.Text)" } else { '' }
        throw "$($Result.Label) failed with exit code $($Result.ExitCode)$detail"
    }
}

function Invoke-Git([string] $Repository, [string[]] $Arguments, [string] $Label) {
    $result = Invoke-NativeCapture -Executable $git -Arguments (@('-C', $Repository) + $Arguments) -Label $Label
    Assert-NativeSuccess $result
    return $result.Text.Trim()
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

function Read-Json([string] $Path, [string] $Label) {
    try {
        return Get-Content -Raw -LiteralPath $Path -Encoding UTF8 | ConvertFrom-Json -Depth 100
    } catch {
        throw "$Label is not valid JSON: $($_.Exception.Message)"
    }
}

function Get-RepositoryIdentity([string] $Repository, [string] $ExpectedCommit, [string] $Label) {
    $root = Resolve-ExistingDirectory $Repository $Label
    $topLevel = Invoke-Git $root @('rev-parse', '--show-toplevel') "$Label Git root inspection"
    Assert-True ([IO.Path]::GetFullPath($topLevel).Equals($root, [StringComparison]::OrdinalIgnoreCase)) "$Label path is not its Git top-level directory"
    $head = (Invoke-Git $root @('rev-parse', '--verify', 'HEAD') "$Label HEAD inspection").ToLowerInvariant()
    $expected = Normalize-Sha256LikeCommit $ExpectedCommit "$Label expected commit"
    Assert-True ($head -ceq $expected) "$Label HEAD differs from the expected commit"
    $status = Invoke-Git $root @('status', '--porcelain=v1', '--untracked-files=all') "$Label clean-tree inspection"
    Assert-True ($status.Length -eq 0) "$Label worktree is not clean"
    $branch = Invoke-Git $root @('rev-parse', '--abbrev-ref', 'HEAD') "$Label branch inspection"
    return [pscustomobject][ordered]@{
        repository = $root
        commit = $head
        branch = $branch
        clean = $true
    }
}

function Normalize-Sha256LikeCommit([string] $Value, [string] $Label) {
    $normalized = $Value.Trim().ToLowerInvariant()
    Assert-True ($normalized -match '^[0-9a-f]{40,64}$') "$Label is not a full Git commit"
    return $normalized
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

function Assert-FunctionalGate([object] $Gate, [string] $ExpectedHost, [string] $ExpectedPlugin) {
    Assert-ExactKeys $Gate @(
        'schema', 'track', 'phase', 'status', 'reportRole', 'startedAtUtc', 'completedAtUtc',
        'evidenceLevels', 'sourceIdentity', 'scope', 'localPython', 'steps', 'claims', 'error'
    ) "$profileLabel functional gate root"
    Assert-True ([int] $Gate.schema -eq 1) 'Functional gate schema is not 1'
    Assert-True ([string] $Gate.track -ceq 'U1') 'Functional gate track is not U1'
    Assert-True ([string] $Gate.phase -ceq $phase) "Functional gate phase is not $phase"
    Assert-True ([string] $Gate.status -ceq 'PASS') 'Functional gate did not pass'
    Assert-True ([string] $Gate.reportRole -ceq $functionalGateRole) 'Functional gate role differs'
    Assert-StringSequence @($Gate.evidenceLevels) @($functionalGateEvidenceLevels) 'Functional gate evidence levels'
    Assert-ExactKeys $Gate.sourceIdentity @('plugin', 'host') 'Functional gate source identity'
    foreach ($definition in @(
        [pscustomobject]@{ Name = 'host'; Commit = $ExpectedHost },
        [pscustomobject]@{ Name = 'plugin'; Commit = $ExpectedPlugin }
    )) {
        $identity = Get-RequiredMember $Gate.sourceIdentity $definition.Name 'Functional gate source identity'
        Assert-ExactKeys $identity @('repository', 'commit', 'dirty', 'changes') "Functional gate $($definition.Name) identity"
        Assert-True ([string] $identity.commit -ceq $definition.Commit) "Functional gate $($definition.Name) commit differs"
        Assert-True ($identity.dirty -eq $false) "Functional gate $($definition.Name) source is dirty"
        Assert-True (@($identity.changes).Count -eq 0) "Functional gate $($definition.Name) changes are non-empty"
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
        Assert-True (-not ([string] $property.Value).Contains([char] 0)) "$Label contains NUL"
    }
}

function Assert-ObservationFixture([object] $Fixture) {
    Assert-ExactKeys $Fixture @(
        'schemaVersion', 'contract', 'track', 'phase', 'runnerComponent',
        'instrumentationArguments', 'selectors'
    ) 'Observation fixture root'
    Assert-True ([int] $Fixture.schemaVersion -eq 1) 'Observation fixture schema is not 1'
    Assert-True ([string] $Fixture.contract -ceq $fixtureContract) 'Observation fixture contract differs'
    Assert-True ([string] $Fixture.track -ceq 'U1' -and [string] $Fixture.phase -ceq $phase) 'Observation fixture track/phase differs'
    Assert-True ([string] $Fixture.runnerComponent -ceq "$hostTestPackage/androidx.test.runner.AndroidJUnitRunner") 'Observation fixture runner component differs'
    Assert-ArgumentObject $Fixture.instrumentationArguments 'Observation fixture global arguments'
    Assert-ExactKeys $Fixture.instrumentationArguments @() 'Observation fixture global arguments'
    $selectors = @($Fixture.selectors)
    Assert-True ($selectors.Count -eq $expectedObservationDefinitions.Count) "Observation fixture selector count differs from the frozen $profileLabel contract"
    $ids = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    $names = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    for ($index = 0; $index -lt $selectors.Count; $index++) {
        $item = $selectors[$index]
        $expectedDefinition = $expectedObservationDefinitions[$index]
        Assert-ExactKeys $item @('id', 'selector', 'arguments', 'covered') 'Observation fixture selector'
        Assert-True ([string] $item.id -match '^[a-z][a-z0-9-]*$') 'Observation fixture selector ID is unsafe'
        Assert-True ($ids.Add([string] $item.id)) 'Observation fixture contains a duplicate selector ID'
        Assert-True ([string] $item.selector -match '^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+#[A-Za-z_][A-Za-z0-9_]*$') 'Observation fixture selector is malformed'
        Assert-True ($names.Add([string] $item.selector)) 'Observation fixture contains a duplicate selector'
        Assert-ArgumentObject $item.arguments "Observation fixture arguments for $($item.id)"
        foreach ($property in $item.arguments.PSObject.Properties) {
            Assert-True ($null -eq $Fixture.instrumentationArguments.PSObject.Properties[$property.Name]) "Selector $($item.id) overrides a global instrumentation argument"
        }
        $covered = @($item.covered)
        Assert-True ($covered.Count -gt 0) "Selector $($item.id) has no coverage labels"
        $uniqueCovered = @($covered | ForEach-Object { [string] $_ } | Sort-Object -Unique)
        Assert-True ($uniqueCovered.Count -eq $covered.Count) "Selector $($item.id) has duplicate coverage labels"
        foreach ($label in $covered) {
            Assert-True ([string] $label -match '^[A-Z][A-Z0-9_]*$') "Selector $($item.id) has an unsafe coverage label"
        }
        Assert-True ([string] $item.id -ceq [string] $expectedDefinition.id) "Observation fixture selector ID differs at index $index"
        Assert-True ([string] $item.selector -ceq [string] $expectedDefinition.selector) "Observation fixture selector differs at index $index"
        Assert-ExactKeys $item.arguments @($expectedDefinition.arguments.Keys) "Observation fixture selector arguments at index $index"
        foreach ($entry in $expectedDefinition.arguments.GetEnumerator()) {
            Assert-True ([string] $item.arguments.PSObject.Properties[$entry.Key].Value -ceq [string] $entry.Value) "Observation fixture selector argument $($entry.Key) differs at index $index"
        }
        Assert-StringSequence @($item.covered) @($expectedDefinition.covered) "Observation fixture coverage at index $index"
    }
}

function Get-ApkSignerEvidence([string] $Path) {
    $result = Invoke-NativeCapture -Executable $script:resolvedApkSigner -Arguments @('verify', '--verbose', '--print-certs', $Path) -Label "apksigner verification for $Path"
    Assert-NativeSuccess $result
    Assert-True ($result.Text -match '(?im)^Verified using v2 scheme \(APK Signature Scheme v2\):\s*true\s*$') "APK v2 signature verification did not pass for $Path"
    $matches = [regex]::Matches(
        $result.Text,
        '(?im)^\s*(?:V\d+\s+)?Signer(?:\s+#?\d+)?\s*:?\s+certificate\s+SHA-256\s+digest:\s*([0-9a-fA-F: ]+)\s*$'
    )
    $digests = @(
        $matches |
            ForEach-Object { Normalize-Sha256 $_.Groups[1].Value "APK signer for $Path" } |
            Sort-Object -Unique
    )
    Assert-True ($digests.Count -eq 1) "APK signer set is not an exact singleton for $Path"
    return [pscustomobject]@{
        Digest = $digests[0]
        V2Verified = $true
        OutputSha256 = Get-TextSha256 $result.Text
    }
}

function Inspect-Apk {
    param(
        [Parameter(Mandatory = $true)] [string] $Role,
        [Parameter(Mandatory = $true)] [string] $Path,
        [Parameter(Mandatory = $true)] [string] $ExpectedSha256,
        [Parameter(Mandatory = $true)] [string] $ExpectedPackage,
        [Parameter(Mandatory = $true)] [bool] $RequireExactAbi
    )
    $resolved = Resolve-ExistingFile $Path "$Role APK"
    $sha256 = Get-FileSha256 $resolved
    Assert-True ($sha256 -ceq (Normalize-Sha256 $ExpectedSha256 "$Role expected SHA-256")) "$Role APK SHA-256 mismatch"
    $badging = Invoke-NativeCapture -Executable $script:resolvedAapt2 -Arguments @('dump', 'badging', $resolved) -Label "aapt2 inspection for $Role"
    Assert-NativeSuccess $badging
    $packageMatch = [regex]::Match($badging.Text, "(?m)^package:\s+name='([^']+)'\s+versionCode='([0-9]*)'\s+versionName='([^']*)'")
    Assert-True $packageMatch.Success "Unable to parse package/version for $Role APK"
    Assert-True ($packageMatch.Groups[1].Value -ceq $ExpectedPackage) "$Role APK package differs"
    $versionCodeText = $packageMatch.Groups[2].Value
    $versionCode = $null
    if ([string]::IsNullOrEmpty($versionCodeText)) {
        Assert-True ($Role -ceq 'androidTest') "$Role APK versionCode is unexpectedly empty"
    } else {
        $parsedVersionCode = 0L
        Assert-True ([long]::TryParse($versionCodeText, [ref] $parsedVersionCode) -and $parsedVersionCode -ge 0L) "$Role APK versionCode is invalid"
        $versionCode = $parsedVersionCode
    }
    $nativeMatch = [regex]::Match($badging.Text, '(?m)^native-code:\s*(.*)$')
    $nativeAbis = if ($nativeMatch.Success) {
        @([regex]::Matches($nativeMatch.Groups[1].Value, "'([^']+)'" ) | ForEach-Object { $_.Groups[1].Value })
    } else {
        @()
    }
    if ($RequireExactAbi) {
        Assert-StringSequence $nativeAbis @($ExpectedAbi) "$Role APK native ABI set"
    }
    $signing = Get-ApkSignerEvidence $resolved
    Assert-True ($signing.Digest -ceq $script:expectedSigner) "$Role APK signer differs from the expected signer"
    return [pscustomobject][ordered]@{
        role = $Role
        path = $resolved
        sizeBytes = [long] (Get-Item -LiteralPath $resolved).Length
        sha256 = $sha256
        packageName = $ExpectedPackage
        versionCode = $versionCode
        versionName = $packageMatch.Groups[3].Value
        nativeAbis = $nativeAbis
        signerSha256 = $signing.Digest
        v2Verified = $true
        debuggable = [bool] ($badging.Text -match '(?m)^application-debuggable(?:\s|$)')
    }
}

function Assert-ArtifactEquivalent([object] $Actual, [object] $Expected, [string] $Label) {
    foreach ($name in @('sizeBytes', 'sha256', 'packageName', 'versionCode', 'versionName', 'signerSha256', 'v2Verified', 'debuggable')) {
        Assert-True ((Get-RequiredMember $Actual $name $Label) -ceq (Get-RequiredMember $Expected $name $Label)) "$Label differs for $name"
    }
    Assert-StringSequence @($Actual.nativeAbis) @($Expected.nativeAbis) "$Label native ABI set"
}

function New-ImmutableArtifactContext([object] $SourceInfo, [string] $TemporaryDirectory, [bool] $RequireExactAbi) {
    $snapshotPath = Join-Path $TemporaryDirectory ("$($SourceInfo.role)-" + [Guid]::NewGuid().ToString('N') + '.apk')
    [IO.File]::Copy($SourceInfo.path, $snapshotPath, $false)
    $snapshotInfo = Inspect-Apk -Role $SourceInfo.role -Path $snapshotPath -ExpectedSha256 $SourceInfo.sha256 -ExpectedPackage $SourceInfo.packageName -RequireExactAbi $RequireExactAbi
    Assert-ArtifactEquivalent $snapshotInfo $SourceInfo "Immutable $($SourceInfo.role) snapshot"
    return [pscustomobject]@{
        Role = $SourceInfo.role
        Info = $SourceInfo
        SnapshotPath = $snapshotPath
        RequireExactAbi = $RequireExactAbi
        InstallAttempted = $false
        InstalledByRun = $false
        InstalledPullVerified = $false
        RemovedByRun = $false
    }
}

function Invoke-ExactAdb([string[]] $Arguments, [string] $Label) {
    return Invoke-NativeCapture -Executable $script:resolvedAdb -Arguments (@('-s', $Serial) + $Arguments) -Label $Label
}

function Get-DeviceProperty([string] $Name, [string] $Label) {
    $result = Invoke-ExactAdb @('shell', 'getprop', $Name) $Label
    Assert-NativeSuccess $result
    $value = $result.Text.Trim()
    Assert-True (-not [string]::IsNullOrWhiteSpace($value)) "$Label returned a blank value"
    return $value
}

function Get-DeviceUserIds {
    $result = Invoke-ExactAdb @('shell', 'pm', 'list', 'users') 'device user inventory'
    Assert-NativeSuccess $result
    $records = [regex]::Matches($result.Text, 'UserInfo\{')
    $matches = [regex]::Matches($result.Text, 'UserInfo\{([0-9]+):')
    Assert-True ($matches.Count -gt 0 -and $matches.Count -eq $records.Count) 'Unable to parse every Android user ID'
    $ids = @($matches | ForEach-Object { [int] $_.Groups[1].Value } | Sort-Object)
    Assert-True (@($ids | Sort-Object -Unique).Count -eq $ids.Count -and 0 -in $ids) 'Android user inventory must contain unique non-negative IDs including user 0'
    return $ids
}

function Get-PackageState([string] $PackageName, [int[]] $UserIds) {
    $userStates = [Collections.Generic.List[object]]::new()
    foreach ($userId in $UserIds) {
        $pathResult = Invoke-ExactAdb @('shell', 'pm', 'path', '--user', "$userId", $PackageName) "package path for $PackageName user $userId"
        Assert-True ($pathResult.ExitCode -in @(0, 1)) "Package path query failed unexpectedly for $PackageName user $userId"
        if ($pathResult.ExitCode -eq 1) {
            Assert-True ([string]::IsNullOrWhiteSpace($pathResult.Text)) "Missing package path query emitted unexpected output for $PackageName user $userId"
        }
        $paths = @(
            $pathResult.Lines |
                Where-Object { $_.StartsWith('package:', [StringComparison]::Ordinal) } |
                ForEach-Object { $_.Substring('package:'.Length) }
        )
        $listResult = Invoke-ExactAdb @('shell', 'pm', 'list', 'packages', '--user', "$userId", $PackageName) "package list for $PackageName user $userId"
        Assert-NativeSuccess $listResult
        $listed = @($listResult.Lines | Where-Object { $_ -ceq "package:$PackageName" }).Count -eq 1
        Assert-True ($listed -eq ($paths.Count -gt 0)) "Inconsistent package state for $PackageName user $userId"
        Assert-True (($listed -and $pathResult.ExitCode -eq 0) -or (-not $listed -and $pathResult.ExitCode -eq 1)) "Package path exit code contradicts package state for $PackageName user $userId"
        $userStates.Add([pscustomobject][ordered]@{
            userId = [int] $userId
            listed = [bool] $listed
            paths = $paths
        })
    }
    $globalResult = Invoke-ExactAdb @('shell', 'pm', 'list', 'packages', '-u', $PackageName) "global package record for $PackageName"
    Assert-NativeSuccess $globalResult
    $globalCount = @($globalResult.Lines | Where-Object { $_ -ceq "package:$PackageName" }).Count
    Assert-True ($globalCount -le 1) "Duplicate global package records for $PackageName"
    return [pscustomobject][ordered]@{
        packageName = $PackageName
        globalRecordCount = [int] $globalCount
        userStates = $userStates.ToArray()
    }
}

function Test-FullyAbsentPackageState([object] $State) {
    return [int] $State.globalRecordCount -eq 0 -and @(
        $State.userStates | Where-Object { $_.listed -or @($_.paths).Count -ne 0 }
    ).Count -eq 0
}

function Assert-FullyAbsentPackageState([object] $State, [string] $Label) {
    Assert-True (Test-FullyAbsentPackageState $State) "$Label must be absent for every frozen user and have no global package record"
}

function Get-RelevantProcesses([string[]] $PackageNames) {
    $result = Invoke-ExactAdb @('shell', 'ps', '-A', '-o', 'NAME') 'device process inventory'
    Assert-NativeSuccess $result
    $names = @(
        $result.Lines |
            ForEach-Object { $_.Trim() } |
            Where-Object {
                $candidate = $_
                -not [string]::IsNullOrWhiteSpace($candidate) -and
                    $candidate -cne 'NAME' -and
                    @($PackageNames | Where-Object {
                        $candidate -ceq $_ -or $candidate.StartsWith("$_`:", [StringComparison]::Ordinal)
                    }).Count -gt 0
            } |
            Sort-Object -Unique
    )
    return $names
}

function Assert-InstalledArtifact([object] $Context, [int[]] $UserIds, [string] $TemporaryDirectory, [string] $Label) {
    $state = Get-PackageState $Context.Info.packageName $UserIds
    $userZero = @($state.userStates | Where-Object { $_.userId -eq 0 })
    $otherInstalled = @($state.userStates | Where-Object { $_.userId -ne 0 -and ($_.listed -or @($_.paths).Count -gt 0) })
    Assert-True (
        $state.globalRecordCount -eq 1 -and
        $userZero.Count -eq 1 -and $userZero[0].listed -and @($userZero[0].paths).Count -eq 1 -and
        $otherInstalled.Count -eq 0
    ) "$Label is not one exact user-0 installation"
    $pullPath = Join-Path $TemporaryDirectory ("pulled-$($Context.Role)-" + [Guid]::NewGuid().ToString('N') + '.apk')
    $pull = Invoke-ExactAdb @('pull', [string] $userZero[0].paths[0], $pullPath) "pull installed $($Context.Role) APK"
    Assert-NativeSuccess $pull
    $pulled = Inspect-Apk -Role $Context.Role -Path $pullPath -ExpectedSha256 $Context.Info.sha256 -ExpectedPackage $Context.Info.packageName -RequireExactAbi $Context.RequireExactAbi
    Assert-ArtifactEquivalent $pulled $Context.Info "$Label pulled APK"
    return $state
}

function Install-Artifact([object] $Context, [int[]] $UserIds, [string] $TemporaryDirectory) {
    $before = Get-PackageState $Context.Info.packageName $UserIds
    Assert-FullyAbsentPackageState $before "Pre-install $($Context.Role) package state"
    $Context.InstallAttempted = $true
    $install = Invoke-ExactAdb @('install', '--user', '0', '-t', $Context.SnapshotPath) "install $($Context.Role) APK"
    Assert-NativeSuccess $install
    Assert-True ($install.Text -match '(?m)^Success\s*$') "Install did not report Success for $($Context.Role)"
    $Context.InstalledByRun = $true
    $null = Assert-InstalledArtifact $Context $UserIds $TemporaryDirectory "Installed $($Context.Role) artifact"
    $Context.InstalledPullVerified = $true
}

function Remove-AttemptedArtifact([object] $Context, [int[]] $UserIds, [string] $TemporaryDirectory) {
    if (-not $Context.InstallAttempted) {
        return
    }
    $current = Get-PackageState $Context.Info.packageName $UserIds
    if (Test-FullyAbsentPackageState $current) {
        $Context.RemovedByRun = $true
        return
    }
    $null = Assert-InstalledArtifact $Context $UserIds $TemporaryDirectory "Runner-owned $($Context.Role) artifact before removal"
    $uninstall = Invoke-ExactAdb @('uninstall', $Context.Info.packageName) "restore $($Context.Role) package state"
    Assert-NativeSuccess $uninstall
    Assert-True ($uninstall.Text -match '(?m)^Success\s*$') "Uninstall did not report Success for $($Context.Role)"
    $restored = Get-PackageState $Context.Info.packageName $UserIds
    Assert-FullyAbsentPackageState $restored "Restored $($Context.Role) package state"
    $Context.RemovedByRun = $true
}

function Add-InstrumentationArguments([Collections.Generic.List[string]] $Arguments, [object] $Values) {
    foreach ($property in @($Values.PSObject.Properties | Sort-Object Name)) {
        $Arguments.Add('-e')
        $Arguments.Add($property.Name)
        $Arguments.Add([string] $property.Value)
    }
}

function New-MergedInstrumentationArguments([object] $FixtureArguments, [object] $SelectorArguments) {
    $merged = [ordered]@{}
    foreach ($values in @($FixtureArguments, $SelectorArguments)) {
        foreach ($property in @($values.PSObject.Properties | Sort-Object Name)) {
            Assert-True (-not $merged.Contains($property.Name)) "Duplicate instrumentation argument $($property.Name)"
            $merged[$property.Name] = [string] $property.Value
        }
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

function Invoke-Observation([object] $Definition, [object] $Fixture) {
    $expectedIdentity = Split-InstrumentationSelector ([string] $Definition.selector)
    $mergedArguments = New-MergedInstrumentationArguments $Fixture.instrumentationArguments $Definition.arguments
    $arguments = [Collections.Generic.List[string]]::new()
    foreach ($value in @('shell', 'am', 'instrument', '--user', '0', '-w', '-r')) {
        $arguments.Add($value)
    }
    $arguments.Add('-e')
    $arguments.Add('class')
    $arguments.Add([string] $Definition.selector)
    Add-InstrumentationArguments $arguments $Fixture.instrumentationArguments
    Add-InstrumentationArguments $arguments $Definition.arguments
    $arguments.Add([string] $Fixture.runnerComponent)
    $result = Invoke-ExactAdb $arguments.ToArray() "instrumentation $($Definition.selector)"
    $outputBytes = Get-Utf8ByteCount $result.Text
    Assert-True ($outputBytes -le $maximumInstrumentationOutputBytes) "Instrumentation output exceeds the 1 MiB evidence bound for $($Definition.selector)"
    $skipMarkers = @(
        'INSTRUMENTATION_STATUS_CODE:\s*-3(?:\s|$)',
        'AssumptionViolatedException',
        '(?im)^INSTRUMENTATION_STATUS:\s+(?:ignored|skipped)=',
        '(?im)\b(?:ignored|skipped)\s*[:=]\s*[1-9][0-9]*\b'
    )
    $hasSkip = @($skipMarkers | Where-Object { $result.Text -match $_ }).Count -gt 0
    $okCount = [regex]::Matches($result.Text, '(?m)^\s*OK \(1 test\)\s*$').Count
    $numTests = @(
        [regex]::Matches($result.Text, '(?m)^INSTRUMENTATION_STATUS:\s*numtests=(\d+)\s*$') |
            ForEach-Object { [int] $_.Groups[1].Value }
    )
    $observedClasses = @(
        [regex]::Matches($result.Text, '(?m)^INSTRUMENTATION_STATUS:\s*class=([^\r\n]+)\s*$') |
            ForEach-Object { $_.Groups[1].Value.Trim() }
    )
    $observedTests = @(
        [regex]::Matches($result.Text, '(?m)^INSTRUMENTATION_STATUS:\s*test=([^\r\n]+)\s*$') |
            ForEach-Object { $_.Groups[1].Value.Trim() }
    )
    $observedClassSet = @($observedClasses | Sort-Object -Unique)
    $observedTestSet = @($observedTests | Sort-Object -Unique)
    $startStatusCount = [regex]::Matches($result.Text, '(?m)^INSTRUMENTATION_STATUS_CODE:\s*1\s*$').Count
    $terminalStatusCount = [regex]::Matches($result.Text, '(?m)^INSTRUMENTATION_STATUS_CODE:\s*0\s*$').Count
    $hasFailure = $result.Text -match '(?m)^(?:FAILURES!!!|INSTRUMENTATION_FAILED:)' -or
        $result.Text -match '(?m)^INSTRUMENTATION_STATUS_CODE:\s*-[124-9][0-9]*\s*$'
    $successCodeCount = [regex]::Matches($result.Text, '(?m)^INSTRUMENTATION_CODE:\s*-1\s*$').Count
    $observedClass = if ($observedClassSet.Count -eq 1) { [string] $observedClassSet[0] } else { '' }
    $observedTest = if ($observedTestSet.Count -eq 1) { [string] $observedTestSet[0] } else { '' }
    $passed = $result.ExitCode -eq 0 -and $okCount -eq 1 -and $numTests.Count -gt 0 -and
        @($numTests | Where-Object { $_ -ne 1 }).Count -eq 0 -and $startStatusCount -eq 1 -and $terminalStatusCount -eq 1 -and
        $successCodeCount -eq 1 -and $observedClasses.Count -ge 2 -and $observedTests.Count -ge 2 -and
        $observedClassSet.Count -eq 1 -and $observedClassSet[0] -ceq $expectedIdentity.ClassName -and
        $observedTestSet.Count -eq 1 -and $observedTestSet[0] -ceq $expectedIdentity.TestName -and
        -not $hasSkip -and -not $hasFailure
    $lastNonBlank = @($result.Lines | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Select-Object -Last 1)
    $record = [pscustomobject][ordered]@{
        id = [string] $Definition.id
        selector = [string] $Definition.selector
        arguments = $mergedArguments
        observedClass = $observedClass
        observedTest = $observedTest
        observedClassRecordCount = [int] $observedClasses.Count
        observedTestRecordCount = [int] $observedTests.Count
        covered = @($Definition.covered)
        startedAtUtc = $result.StartedAtUtc
        completedAtUtc = $result.CompletedAtUtc
        elapsedMillis = $result.ElapsedMillis
        exitCode = $result.ExitCode
        output = $result.Text
        outputUtf8Bytes = $outputBytes
        outputSha256 = Get-TextSha256 $result.Text
        outputLineCount = [int] $result.Lines.Count
        lastNonBlankLine = if ($lastNonBlank.Count -eq 1) { [string] $lastNonBlank[0] } else { '' }
        okCount = [int] $okCount
        startStatusCount = [int] $startStatusCount
        terminalStatusCount = [int] $terminalStatusCount
        successCodeCount = [int] $successCodeCount
        result = if ($passed) { 'OK_1_TEST_ZERO_SKIP' } else { 'FAILED' }
    }
    return [pscustomobject]@{
        Record = $record
        Passed = $passed
    }
}

function Get-ToolRecord([string] $Path, [string[]] $VersionArguments, [string] $Label) {
    $result = Invoke-NativeCapture -Executable $Path -Arguments $VersionArguments -Label "$Label version inspection"
    Assert-NativeSuccess $result
    return [pscustomobject][ordered]@{
        path = $Path
        sizeBytes = [long] (Get-Item -LiteralPath $Path).Length
        sha256 = Get-FileSha256 $Path
        versionOutputSha256 = Get-TextSha256 $result.Text
    }
}

function Resolve-NewRawOutput([string] $Path, [string] $Repository) {
    $reportsRoot = [IO.Path]::GetFullPath((Join-Path $Repository 'build/reports/python/u1'))
    $reportsPrefix = $reportsRoot.TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar
    $fullPath = [IO.Path]::GetFullPath($Path)
    Assert-True ($fullPath.StartsWith($reportsPrefix, [StringComparison]::OrdinalIgnoreCase)) 'Raw output must be below build/reports/python/u1'
    Assert-True ([IO.Path]::GetFileName($fullPath).StartsWith($rawOutputPrefix, [StringComparison]::Ordinal)) "Raw output filename must begin with $rawOutputPrefix"
    Assert-True ([IO.Path]::GetExtension($fullPath) -ceq '.json') 'Raw output must use the .json extension'
    Assert-True (-not (Test-Path -LiteralPath $fullPath)) 'Raw output already exists and will not be overwritten'
    $relative = $fullPath.Substring($Repository.Length).TrimStart('\', '/').Replace('\', '/')
    $ignored = Invoke-NativeCapture -Executable $git -Arguments @('-C', $Repository, 'check-ignore', '--quiet', '--no-index', '--', $relative) -Label 'raw output ignore-policy inspection'
    Assert-NativeSuccess $ignored
    return $fullPath
}

function Write-NewJson([string] $Path, [object] $Value) {
    $directory = [IO.Path]::GetDirectoryName($Path)
    [void] [IO.Directory]::CreateDirectory($directory)
    $temporary = Join-Path $directory ('.' + [IO.Path]::GetFileName($Path) + '.' + [Guid]::NewGuid().ToString('N') + '.tmp')
    try {
        [IO.File]::WriteAllText($temporary, (($Value | ConvertTo-Json -Depth 30) + "`n"), $utf8WithoutBom)
        Assert-True (-not (Test-Path -LiteralPath $Path)) 'Raw output appeared concurrently and will not be overwritten'
        [IO.File]::Move($temporary, $Path)
    } finally {
        if (Test-Path -LiteralPath $temporary -PathType Leaf) {
            Remove-Item -LiteralPath $temporary -Force
        }
    }
}

function New-Claims([bool] $DevicePass) {
    if ($isR2Profile) {
        return [pscustomobject][ordered]@{
            portableTestsPassed = $true
            androidCompiled = $true
            apkPackaged = $true
            binderExecuted = $DevicePass
            packagedCpythonExecuted = $DevicePass
            deviceVerified = $DevicePass
            moduleEntryVerified = $DevicePass
            executionTimeStreamingVerified = $DevicePass
            interactiveInputVerified = $DevicePass
            structuredJsonVerified = $DevicePass
            outputArtifactsVerified = $DevicePass
            resultLimitRecoveryVerified = $DevicePass
            cancellationRecoveryVerified = $DevicePass
            timeoutRecoveryVerified = $DevicePass
            restorationVerified = $DevicePass
            deviceMatrixVerified = $false
            productionEvidence = $false
            published = $false
            releaseAuthorized = $false
        }
    }
    return [pscustomobject][ordered]@{
        portableTestsPassed = $true
        androidCompiled = $true
        apkPackaged = $true
        binderExecuted = $DevicePass
        packagedCpythonExecuted = $DevicePass
        deviceVerified = $DevicePass
        stdinVerified = $DevicePass
        importsVerified = $DevicePass
        sequentialIsolationVerified = $DevicePass
        restorationVerified = $DevicePass
        deviceMatrixVerified = $false
        productionEvidence = $false
        published = $false
        releaseAuthorized = $false
    }
}

if (-not $ConfirmNoActiveSoak.IsPresent) {
    throw 'Pass -ConfirmNoActiveSoak explicitly; the runner must not touch a device in an active soak'
}
if (-not $ConfirmDeviceMutation.IsPresent) {
    throw 'Pass -ConfirmDeviceMutation explicitly; temporary package installation is otherwise forbidden'
}
if ($Serial.StartsWith('-', [StringComparison]::Ordinal)) {
    throw 'Serial must not begin with a dash'
}
if (-not [string]::IsNullOrWhiteSpace($env:ANDROID_SERIAL) -and $env:ANDROID_SERIAL -cne $Serial) {
    throw 'ANDROID_SERIAL differs from -Serial; refusing ambiguous device scope'
}

$expectedUsers = @($ExpectedUserIds | Sort-Object)
Assert-True ($expectedUsers.Count -eq $ExpectedUserIds.Count -and @($expectedUsers | Sort-Object -Unique).Count -eq $expectedUsers.Count) 'ExpectedUserIds contains duplicates'
Assert-True (@($expectedUsers | Where-Object { $_ -lt 0 }).Count -eq 0 -and 0 -in $expectedUsers) 'ExpectedUserIds must contain unique non-negative IDs including user 0'
$expectedHost = Normalize-Sha256LikeCommit $ExpectedHostCommit 'Expected Host commit'
$expectedPlugin = Normalize-Sha256LikeCommit $ExpectedPluginCommit 'Expected Plugin commit'
$script:expectedSigner = Normalize-Sha256 $ExpectedSignerSha256 'Expected signer SHA-256'
$script:resolvedAdb = Resolve-ExistingFile $AdbPath 'adb'
$script:resolvedAapt2 = Resolve-ExistingFile $Aapt2Path 'aapt2'
$script:resolvedApkSigner = Resolve-ExistingFile $ApkSignerPath 'apksigner'
Assert-True ([IO.Path]::GetFileName($script:resolvedAdb) -in @('adb.exe', 'adb')) 'AdbPath must identify adb or adb.exe explicitly'
Assert-True ([IO.Path]::GetFileName($script:resolvedAapt2) -in @('aapt2.exe', 'aapt2')) 'Aapt2Path must identify aapt2 or aapt2.exe explicitly'
Assert-True ([IO.Path]::GetFileName($script:resolvedApkSigner) -in @('apksigner.bat', 'apksigner.exe', 'apksigner')) 'ApkSignerPath must identify apksigner explicitly'

$mutexName = 'Global\AutoJs6-Codex-Device-' + ([regex]::Replace($Serial, '[^A-Za-z0-9_.-]', '_'))

$hostIdentity = Get-RepositoryIdentity $HostRepository $expectedHost 'Host repository'
$pluginIdentity = Get-RepositoryIdentity $PluginRepository $expectedPlugin 'Plugin repository'
$scriptRepository = [IO.Path]::GetFullPath((Split-Path -Parent (Split-Path -Parent $PSScriptRoot))).TrimEnd('\', '/')
Assert-True ($pluginIdentity.repository.Equals($scriptRepository, [StringComparison]::OrdinalIgnoreCase)) 'PluginRepository differs from the repository containing this runner'
$rawOutput = Resolve-NewRawOutput $Output $pluginIdentity.repository

$functionalGatePath = Resolve-ExistingFile $FunctionalGate "$profileLabel functional gate"
$functionalGateDigest = Normalize-Sha256 $FunctionalGateSha256 'Functional gate SHA-256'
Assert-True ((Get-FileSha256 $functionalGatePath) -ceq $functionalGateDigest) 'Functional gate SHA-256 mismatch'
$functionalGateJson = Read-Json $functionalGatePath "$profileLabel functional gate"
Assert-FunctionalGate $functionalGateJson $expectedHost $expectedPlugin

$fixturePath = Resolve-ExistingFile $ObservationFixture "$profileLabel observation fixture"
$fixtureDigest = Normalize-Sha256 $ObservationFixtureSha256 'Observation fixture SHA-256'
$canonicalFixturePath = [IO.Path]::GetFullPath((Join-Path $pluginIdentity.repository $fixtureRelativePath))
$canonicalFixtureMessage = if ($isR2Profile) { 'Observation fixture must be the canonical tracked U1-R2 contract' } else { 'Observation fixture must be the canonical tracked U1-R1 contract' }
Assert-True ($fixturePath.Equals($canonicalFixturePath, [StringComparison]::OrdinalIgnoreCase)) $canonicalFixtureMessage
Assert-True ((Get-FileSha256 $fixturePath) -ceq $fixtureDigest) 'Observation fixture SHA-256 mismatch'
$fixture = Read-Json $fixturePath "$profileLabel observation fixture"
Assert-ObservationFixture $fixture

$hostInfo = Inspect-Apk -Role 'host' -Path $HostApk -ExpectedSha256 $HostSha256 -ExpectedPackage $hostPackage -RequireExactAbi $true
$testInfo = Inspect-Apk -Role 'androidTest' -Path $HostTestApk -ExpectedSha256 $HostTestSha256 -ExpectedPackage $hostTestPackage -RequireExactAbi $false
$pluginInfo = Inspect-Apk -Role 'plugin' -Path $PluginApk -ExpectedSha256 $PluginSha256 -ExpectedPackage $pluginPackage -RequireExactAbi $true

$deviceMutex = [Threading.Mutex]::new($false, $mutexName)
$deviceMutexOwned = $false
try {
    try {
        $deviceMutexOwned = $deviceMutex.WaitOne(0)
    } catch [Threading.AbandonedMutexException] {
        $deviceMutexOwned = $true
    }
    Assert-True $deviceMutexOwned "Another exact-device transaction owns mutex $mutexName"
    Assert-NoCompetingDeviceOrGradleClient

$tools = [pscustomobject][ordered]@{
    adb = Get-ToolRecord $script:resolvedAdb @('version') 'adb'
    aapt2 = Get-ToolRecord $script:resolvedAapt2 @('version') 'aapt2'
    apkSigner = Get-ToolRecord $script:resolvedApkSigner @('version') 'apksigner'
}

$temporaryRoot = Join-Path ([IO.Path]::GetTempPath()) ("autojs6-python-u1-$($phase.ToLowerInvariant())-e3-" + [Guid]::NewGuid().ToString('N'))
[void] [IO.Directory]::CreateDirectory($temporaryRoot)
$contexts = @(
    New-ImmutableArtifactContext $hostInfo $temporaryRoot $true
    New-ImmutableArtifactContext $pluginInfo $temporaryRoot $true
    New-ImmutableArtifactContext $testInfo $temporaryRoot $false
)
$observations = [Collections.Generic.List[object]]::new()
$restorationErrors = [Collections.Generic.List[string]]::new()
$primaryFailure = $null
$deviceStateText = 'NOT_COMPLETED'
$deviceApi = $null
$deviceAbi = $null
$deviceAbiList = @()
$deviceFingerprint = $null
$frozenUsers = @()
$initialStates = $null
$initialProcesses = @()
$finalStates = $null
$finalProcesses = @()
$devicePreflightComplete = $false
$userInventoryUnchanged = $false
$packagesRestored = $false
$processesClean = $false

try {
    $deviceState = Invoke-ExactAdb @('get-state') 'exact device state'
    Assert-NativeSuccess $deviceState
    $deviceStateText = $deviceState.Text.Trim()
    Assert-True ($deviceStateText -ceq 'device') "Exact serial is not in device state: $deviceStateText"
    $deviceApiText = Get-DeviceProperty 'ro.build.version.sdk' 'device API query'
    $parsedApi = 0
    Assert-True ([int]::TryParse($deviceApiText, [ref] $parsedApi)) 'Device API is not an integer'
    $deviceApi = $parsedApi
    Assert-True ($deviceApi -eq $ExpectedApi) "Device API differs: expected=$ExpectedApi actual=$deviceApi"
    $deviceAbi = (Get-DeviceProperty 'ro.product.cpu.abi' 'device primary ABI query').Trim()
    Assert-True ($deviceAbi -ceq $ExpectedAbi) "Device ABI differs: expected=$ExpectedAbi actual=$deviceAbi"
    $deviceAbiList = @((Get-DeviceProperty 'ro.product.cpu.abilist' 'device ABI list query').Split(',') | ForEach-Object { $_.Trim() } | Where-Object { $_.Length -gt 0 })
    Assert-True ($ExpectedAbi -in $deviceAbiList) 'Expected ABI is absent from the device ABI list'
    $deviceFingerprint = Get-DeviceProperty 'ro.build.fingerprint' 'device fingerprint query'
    $frozenUsers = @(Get-DeviceUserIds)
    Assert-IntSequence $frozenUsers $expectedUsers 'Exact device user inventory'
    $initialStates = [pscustomobject][ordered]@{
        host = Get-PackageState $hostPackage $frozenUsers
        androidTest = Get-PackageState $hostTestPackage $frozenUsers
        plugin = Get-PackageState $pluginPackage $frozenUsers
    }
    foreach ($name in @('host', 'androidTest', 'plugin')) {
        Assert-FullyAbsentPackageState (Get-RequiredMember $initialStates $name 'Initial package states') "Initial $name package state"
    }
    $initialProcesses = @(Get-RelevantProcesses @($hostPackage, $hostTestPackage, $pluginPackage))
    Assert-True ($initialProcesses.Count -eq 0) 'Relevant package processes exist before installation'
    $devicePreflightComplete = $true

    foreach ($context in $contexts) {
        Assert-IntSequence @(Get-DeviceUserIds) $frozenUsers 'Device user inventory before install'
        Install-Artifact $context $frozenUsers $temporaryRoot
    }
    foreach ($definition in @($fixture.selectors)) {
        Assert-IntSequence @(Get-DeviceUserIds) $frozenUsers 'Device user inventory before observation'
        $outcome = Invoke-Observation $definition $fixture
        $observations.Add($outcome.Record)
        Assert-True $outcome.Passed "Instrumentation did not prove exactly OK (1 test), zero skips: $($definition.selector)"
    }
} catch {
    $primaryFailure = $_.Exception
} finally {
    if ($devicePreflightComplete) {
        for ($index = $contexts.Count - 1; $index -ge 0; $index--) {
            try {
                Remove-AttemptedArtifact $contexts[$index] $frozenUsers $temporaryRoot
            } catch {
                $restorationErrors.Add($_.Exception.Message)
            }
        }
        try {
            Assert-IntSequence @(Get-DeviceUserIds) $frozenUsers 'Final device user inventory'
            $userInventoryUnchanged = $true
            $finalStates = [pscustomobject][ordered]@{
                host = Get-PackageState $hostPackage $frozenUsers
                androidTest = Get-PackageState $hostTestPackage $frozenUsers
                plugin = Get-PackageState $pluginPackage $frozenUsers
            }
            foreach ($name in @('host', 'androidTest', 'plugin')) {
                Assert-FullyAbsentPackageState (Get-RequiredMember $finalStates $name 'Final package states') "Final $name package state"
            }
            $packagesRestored = $true
        } catch {
            $restorationErrors.Add($_.Exception.Message)
        }
        try {
            for ($attempt = 0; $attempt -lt 20; $attempt++) {
                $finalProcesses = @(Get-RelevantProcesses @($hostPackage, $hostTestPackage, $pluginPackage))
                if ($finalProcesses.Count -eq 0) { break }
                Start-Sleep -Milliseconds 250
            }
            Assert-True ($finalProcesses.Count -eq 0) "Relevant processes remain after restoration: $($finalProcesses -join ',')"
            $processesClean = $true
        } catch {
            $restorationErrors.Add($_.Exception.Message)
        }
    }
    try {
        $null = Get-RepositoryIdentity $hostIdentity.repository $expectedHost 'Post-run Host repository'
        $null = Get-RepositoryIdentity $pluginIdentity.repository $expectedPlugin 'Post-run Plugin repository'
        Assert-True ((Get-FileSha256 $functionalGatePath) -ceq $functionalGateDigest) 'Functional gate changed during the run'
        Assert-True ((Get-FileSha256 $fixturePath) -ceq $fixtureDigest) 'Observation fixture changed during the run'
        foreach ($info in @($hostInfo, $testInfo, $pluginInfo)) {
            Assert-True ((Get-FileSha256 $info.path) -ceq $info.sha256) "$($info.role) source APK changed during the run"
        }
    } catch {
        $restorationErrors.Add($_.Exception.Message)
    }
    try {
        $tempPrefix = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd('\', '/') + [IO.Path]::DirectorySeparatorChar
        $resolvedTemporaryRoot = [IO.Path]::GetFullPath($temporaryRoot)
        Assert-True ($resolvedTemporaryRoot.StartsWith($tempPrefix, [StringComparison]::OrdinalIgnoreCase)) 'Temporary evidence directory escaped the system temporary root'
        if (Test-Path -LiteralPath $resolvedTemporaryRoot -PathType Container) {
            [IO.Directory]::Delete($resolvedTemporaryRoot, $true)
        }
    } catch {
        $restorationErrors.Add("Local immutable snapshot cleanup failed: $($_.Exception.Message)")
    }
}

$allObservationsPassed = $observations.Count -eq @($fixture.selectors).Count -and @($observations | Where-Object { $_.result -cne 'OK_1_TEST_ZERO_SKIP' }).Count -eq 0
$restorationVerified = $devicePreflightComplete -and $restorationErrors.Count -eq 0 -and $userInventoryUnchanged -and $packagesRestored -and $processesClean
$devicePass = $null -eq $primaryFailure -and $allObservationsPassed -and $restorationVerified
$status = if ($restorationErrors.Count -gt 0) { 'FAILED_RESTORATION' } elseif ($devicePass) { 'PASS' } else { 'FAILED' }
$report = [pscustomobject][ordered]@{
    schemaVersion = 1
    createdAtUtc = [DateTimeOffset]::UtcNow.ToString('o')
    status = $status
    scope = $rawScope
    evidenceLevel = if ($devicePass) { $evidenceLevel } else { 'NOT_ESTABLISHED' }
    source = [pscustomobject][ordered]@{
        host = $hostIdentity
        plugin = $pluginIdentity
    }
    functionalGate = [pscustomobject][ordered]@{
        path = $functionalGatePath
        sizeBytes = [long] (Get-Item -LiteralPath $functionalGatePath).Length
        sha256 = $functionalGateDigest
        status = 'PASS'
        reportRole = $functionalGateRole
    }
    observationContract = [pscustomobject][ordered]@{
        path = $fixturePath
        sizeBytes = [long] (Get-Item -LiteralPath $fixturePath).Length
        sha256 = $fixtureDigest
        schemaVersion = 1
    }
    artifacts = [pscustomobject][ordered]@{
        host = $hostInfo
        androidTest = $testInfo
        plugin = $pluginInfo
    }
    tools = $tools
    device = [pscustomobject][ordered]@{
        serial = $Serial
        api = $deviceApi
        abi = $deviceAbi
        abiList = $deviceAbiList
        fingerprint = $deviceFingerprint
        frozenUserIds = $frozenUsers
    }
    preflight = [pscustomobject][ordered]@{
        confirmNoActiveSoak = $ConfirmNoActiveSoak.IsPresent
        confirmDeviceMutation = $ConfirmDeviceMutation.IsPresent
        mutexName = $mutexName
        deviceState = $deviceStateText
        userInventory = $frozenUsers
        initialPackageStates = $initialStates
        relevantProcesses = $initialProcesses
    }
    observations = $observations.ToArray()
    restoration = [pscustomobject][ordered]@{
        verified = $restorationVerified
        userInventoryUnchanged = $userInventoryUnchanged
        packagesRestored = $packagesRestored
        processesClean = $processesClean
        temporaryInstalls = @($contexts | ForEach-Object {
            [pscustomobject][ordered]@{
                role = $_.Role
                packageName = $_.Info.packageName
                installAttempted = [bool] $_.InstallAttempted
                installedByRun = [bool] $_.InstalledByRun
                installedPullVerified = [bool] $_.InstalledPullVerified
                removedByRun = [bool] $_.RemovedByRun
            }
        })
        finalPackageStates = $finalStates
        finalRelevantProcesses = $finalProcesses
        errors = $restorationErrors.ToArray()
    }
    claims = New-Claims $devicePass
    limitations = $limitations
    error = if ($null -eq $primaryFailure) { $null } else { $primaryFailure.Message }
}
Write-NewJson $rawOutput $report
$rawSha256 = Get-FileSha256 $rawOutput
Write-Output "U1_$($phase)_DEVICE_RAW_STATUS=$status"
Write-Output "OUTPUT=$rawOutput"
Write-Output "OUTPUT_SHA256=$rawSha256"
if (-not $devicePass) {
    $detail = if ($restorationErrors.Count -gt 0) { [string]::Join("`n", $restorationErrors) } elseif ($null -ne $primaryFailure) { $primaryFailure.Message } else { 'Required observations did not pass' }
    throw "$profileLabel device evidence did not pass: $status`n$detail"
}
} finally {
    if ($deviceMutexOwned) {
        $deviceMutex.ReleaseMutex()
    }
    $deviceMutex.Dispose()
}
