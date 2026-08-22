param(
    [string]$PythonExecutable = 'python',
    [Parameter(Mandatory = $true)]
    [string]$HostRepository
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$repoRoot = Split-Path -Parent $PSScriptRoot
$reportRelative = 'build/reports/python/u1/r2-structured-results-contract.json'
$reportPath = Join-Path $repoRoot $reportRelative
$steps = [ordered]@{}
$failureMessage = $null
$startedAtUtc = [DateTime]::UtcNow
$pythonVersion = $null

function Assert-True([bool]$Condition, [string]$Message) {
    if (-not $Condition) {
        throw $Message
    }
}

function Get-TextSha256([string]$Text) {
    $bytes = [Text.Encoding]::UTF8.GetBytes($Text)
    $algorithm = [Security.Cryptography.SHA256]::Create()
    try {
        return -join ($algorithm.ComputeHash($bytes) | ForEach-Object { $_.ToString('x2') })
    }
    finally {
        $algorithm.Dispose()
    }
}

function Convert-NativeLine($Line) {
    if ($Line -is [Management.Automation.ErrorRecord]) {
        return $Line.ToString()
    }
    return [string]$Line
}

function Invoke-RecordedStep(
    [string]$Name,
    [string]$Executable,
    [string[]]$Arguments,
    [string]$WorkingDirectory
) {
    $timer = [Diagnostics.Stopwatch]::StartNew()
    $previousLocation = Get-Location
    $previousErrorAction = $ErrorActionPreference
    try {
        Set-Location -LiteralPath $WorkingDirectory
        $ErrorActionPreference = 'Continue'
        $rawOutput = @(& $Executable @Arguments 2>&1)
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorAction
        Set-Location -LiteralPath $previousLocation
        $timer.Stop()
    }
    $output = @($rawOutput | ForEach-Object { Convert-NativeLine $_ })
    $output | ForEach-Object { Write-Host $_ }
    $joinedOutput = ($output -join "`n") + "`n"
    $record = [ordered]@{
        name = $Name
        executable = $Executable
        arguments = $Arguments
        workingDirectory = $WorkingDirectory
        exitCode = $exitCode
        passed = $exitCode -eq 0
        elapsedMillis = $timer.ElapsedMilliseconds
        outputLineCount = $output.Count
        outputSha256 = Get-TextSha256 $joinedOutput
        lastOutputLine = if ($output.Count -eq 0) { $null } else { [string]$output[-1] }
    }
    $steps[$Name] = $record
    Assert-True ($exitCode -eq 0) "$Name failed with exit code $exitCode"
    return $record
}

function Invoke-GitLines([string]$Repository, [string[]]$Arguments) {
    $previousErrorAction = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $raw = @(& git -C $Repository @Arguments 2>&1)
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorAction
    }
    Assert-True ($exitCode -eq 0) 'Git source-identity query failed'
    return @($raw | ForEach-Object { Convert-NativeLine $_ })
}

function Get-SourceIdentity([string]$Repository) {
    $head = (Invoke-GitLines $Repository @('rev-parse', 'HEAD') | Select-Object -Last 1).Trim()
    Assert-True ($head -match '^[0-9a-f]{40}$') "Invalid Git HEAD in $Repository"
    $changes = @(
        Invoke-GitLines $Repository @('status', '--porcelain=v1', '--untracked-files=all') |
            Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
    )
    return [ordered]@{
        repository = $Repository
        commit = $head
        dirty = $changes.Count -ne 0
        changes = $changes
    }
}

$resolvedHostRepository = $null
$pluginIdentity = $null
$hostIdentity = $null

try {
    $gradle = Join-Path $repoRoot 'gradlew.bat'
    Assert-True (Test-Path -LiteralPath $gradle -PathType Leaf) 'Plugin Gradle wrapper is missing'
    Assert-True (-not [string]::IsNullOrWhiteSpace($HostRepository)) 'Host repository is required'
    $resolvedHostRepository = (Resolve-Path -LiteralPath $HostRepository).Path
    $hostGradle = Join-Path $resolvedHostRepository 'gradlew.bat'
    Assert-True (Test-Path -LiteralPath $hostGradle -PathType Leaf) 'Host Gradle wrapper is missing'
    Assert-True (
        Test-Path -LiteralPath (
            Join-Path $resolvedHostRepository 'plugin-api/python-runtime-api'
        ) -PathType Container
    ) 'Host python-runtime-api module is missing'

    $versionStep = Invoke-RecordedStep `
        'localPythonVersion' `
        $PythonExecutable `
        @('-B', '-c', 'import platform; print(platform.python_version())') `
        $repoRoot
    $pythonVersion = [string]$versionStep.lastOutputLine

    Invoke-RecordedStep `
        'portablePythonAndSourceTests' `
        $PythonExecutable `
        @('-B', '-m', 'unittest', 'discover', '-s', 'tools/tests', '-p', 'test_*.py', '-v') `
        $repoRoot | Out-Null

    Invoke-RecordedStep `
        'pluginJvmAndAndroidBuild' `
        $gradle `
        @('--console=plain', '--no-parallel', ':app:testDebugUnitTest', ':app:assembleDebug') `
        $repoRoot | Out-Null

    Invoke-RecordedStep `
        'trackedDiffCheck' `
        'git' `
        @('diff', '--check') `
        $repoRoot | Out-Null

    Invoke-RecordedStep `
        'hostPythonApiTests' `
        $hostGradle `
        @(
            '--console=plain',
            '--no-parallel',
            ':plugin-api:python-runtime-api:testDebugUnitTest'
        ) `
        $resolvedHostRepository | Out-Null

    Invoke-RecordedStep `
        'hostTargetedStructuredResultTests' `
        $hostGradle `
        @(
            '--console=plain',
            '--no-parallel',
            ':app:testAppDebugUnitTest',
            '--tests', '*PythonRuntimeExecutionResultTest',
            '--tests', '*PythonRuntimeProviderSelectionPolicyTest',
            '--tests', '*PythonRuntimeHostPlanningTest'
        ) `
        $resolvedHostRepository | Out-Null

    Invoke-RecordedStep `
        'hostTrackedDiffCheck' `
        'git' `
        @('-C', $resolvedHostRepository, 'diff', '--check') `
        $resolvedHostRepository | Out-Null

    $pluginIdentity = Get-SourceIdentity $repoRoot
    $hostIdentity = Get-SourceIdentity $resolvedHostRepository
}
catch {
    $failureMessage = $_.Exception.Message
    if ($null -eq $pluginIdentity) {
        try { $pluginIdentity = Get-SourceIdentity $repoRoot } catch { }
    }
    if ($null -ne $resolvedHostRepository -and $null -eq $hostIdentity) {
        try { $hostIdentity = Get-SourceIdentity $resolvedHostRepository } catch { }
    }
}

$portablePassed = $steps.Contains('portablePythonAndSourceTests') -and
    [bool]$steps['portablePythonAndSourceTests'].passed
$pluginBuildPassed = $steps.Contains('pluginJvmAndAndroidBuild') -and
    [bool]$steps['pluginJvmAndAndroidBuild'].passed
$pluginDiffPassed = $steps.Contains('trackedDiffCheck') -and
    [bool]$steps['trackedDiffCheck'].passed
$pluginFunctionalPassed = $portablePassed -and $pluginBuildPassed -and $pluginDiffPassed
$hostApiPassed = $steps.Contains('hostPythonApiTests') -and
    [bool]$steps['hostPythonApiTests'].passed
$hostAppPassed = $steps.Contains('hostTargetedStructuredResultTests') -and
    [bool]$steps['hostTargetedStructuredResultTests'].passed
$hostDiffPassed = $steps.Contains('hostTrackedDiffCheck') -and
    [bool]$steps['hostTrackedDiffCheck'].passed
$hostScopedEvidencePassed = $hostApiPassed -and $hostAppPassed -and $hostDiffPassed
$passed = $null -eq $failureMessage -and $pluginFunctionalPassed -and $hostScopedEvidencePassed
$evidenceLevels = @('PORTABLE_CPYTHON_ONLY', 'ANDROID_BUILD_ONLY')
if ($hostScopedEvidencePassed) {
    $evidenceLevels += 'HOST_PYTHON_JVM_TARGETED_ONLY'
}

$report = [ordered]@{
    schema = 1
    track = 'U1'
    phase = 'R2-STRUCTURED-RESULTS'
    status = if ($passed) { 'PASS' } else { 'FAIL' }
    phaseStatus = 'PARTIAL'
    reportRole = 'CURRENT_TREE_R2_STRUCTURED_RESULTS_PARTIAL_FUNCTIONAL_GATE'
    startedAtUtc = $startedAtUtc.ToString('o')
    completedAtUtc = [DateTime]::UtcNow.ToString('o')
    evidenceLevels = $evidenceLevels
    sourceIdentity = [ordered]@{
        plugin = $pluginIdentity
        host = $hostIdentity
    }
    localPython = [ordered]@{
        executable = $PythonExecutable
        version = $pythonVersion
        exactPackagedTargetVersion = $pythonVersion -ceq '3.13.9'
    }
    scope = [ordered]@{
        protocolMinor14 = $hostScopedEvidencePassed
        goldenWireCompatibility = $hostApiPassed
        explicitResultApi = $pluginFunctionalPassed
        stdoutResultInferenceForbidden = $pluginFunctionalPassed -and $hostScopedEvidencePassed
        structuredJsonResult = $pluginFunctionalPassed -and $hostScopedEvidencePassed
        strictCanonicalJson = $pluginFunctionalPassed -and $hostScopedEvidencePassed
        outputArtifacts = $pluginFunctionalPassed -and $hostScopedEvidencePassed
        artifactCountPathAndSizeLimits = $pluginFunctionalPassed -and $hostScopedEvidencePassed
        immutablePluginSnapshots = $pluginFunctionalPassed
        exactLengthAndSha256HostReceive = $hostScopedEvidencePassed
        descriptorReferencesExact = $hostApiPassed
        terminalCleanupBound = $pluginFunctionalPassed -and $hostScopedEvidencePassed
        hostReleaseAarLocked = $pluginFunctionalPassed
        r2Complete = $false
    }
    steps = $steps
    claims = [ordered]@{
        portableTestsPassed = $portablePassed
        androidCompiled = $pluginBuildPassed
        apkPackaged = $pluginBuildPassed
        hostApiChanged = $true
        hostRequested = $true
        hostChecked = $hostScopedEvidencePassed
        hostCheckScope = 'PYTHON_API_ALL_AND_STRUCTURED_RESULT_APP_TARGETS_ONLY'
        hostFullAppSuiteExecuted = $false
        binderExecuted = $false
        deviceVerified = $false
        productionEvidence = $false
        published = $false
        releaseAuthorized = $false
    }
    error = $failureMessage
}

$reportDirectory = Split-Path -Parent $reportPath
[IO.Directory]::CreateDirectory($reportDirectory) | Out-Null
$temporaryPath = "$reportPath.tmp"
$utf8NoBom = New-Object Text.UTF8Encoding($false)
[IO.File]::WriteAllText(
    $temporaryPath,
    (($report | ConvertTo-Json -Depth 14) + "`n"),
    $utf8NoBom
)
Move-Item -LiteralPath $temporaryPath -Destination $reportPath -Force

if (-not $passed) {
    $detail = if ($null -eq $failureMessage) { 'one or more required scopes did not pass' } else { $failureMessage }
    throw "U1-R2 structured-results sub-gate failed: $detail; report=$reportRelative"
}

Write-Host (
    "U1-R2 structured-results sub-gate passed: portable=true androidBuild=true " +
    "hostTargeted=true r2Complete=false device=false report=$reportRelative"
)
