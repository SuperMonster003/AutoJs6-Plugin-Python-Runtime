#Requires -Version 7.0

[CmdletBinding()]
param(
    [string] $PythonExecutable = 'python',

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $HostRepository
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false

$repoRoot = [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot)).TrimEnd('\', '/')
$resolvedHostRepository = [IO.Path]::GetFullPath((Resolve-Path -LiteralPath $HostRepository).Path).TrimEnd('\', '/')
$reportRelative = 'build/reports/python/u1/r2-e3-functional-gate.json'
$reportPath = Join-Path $repoRoot $reportRelative
$steps = [ordered]@{}
$contracts = [ordered]@{}
$failureMessage = $null
$startedAtUtc = [DateTimeOffset]::UtcNow
$pythonVersion = $null
$pluginIdentity = $null
$hostIdentity = $null
$utf8WithoutBom = [Text.UTF8Encoding]::new($false)

function Assert-True([bool] $Condition, [string] $Message) {
    if (-not $Condition) { throw $Message }
}

function Get-TextSha256([string] $Text) {
    $algorithm = [Security.Cryptography.SHA256]::Create()
    try {
        return [Convert]::ToHexString($algorithm.ComputeHash($utf8WithoutBom.GetBytes($Text))).ToLowerInvariant()
    } finally {
        $algorithm.Dispose()
    }
}

function Get-FileSha256([string] $Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Convert-NativeLine([object] $Line) {
    if ($Line -is [Management.Automation.ErrorRecord]) { return $Line.ToString() }
    return [string] $Line
}

function Invoke-RecordedStep {
    param(
        [Parameter(Mandatory = $true)] [string] $Name,
        [Parameter(Mandatory = $true)] [string] $Executable,
        [Parameter(Mandatory = $true)] [string[]] $Arguments,
        [Parameter(Mandatory = $true)] [string] $WorkingDirectory
    )
    $timer = [Diagnostics.Stopwatch]::StartNew()
    $previousLocation = Get-Location
    $previousPreference = $ErrorActionPreference
    $raw = @()
    $exitCode = -1
    try {
        Set-Location -LiteralPath $WorkingDirectory
        $ErrorActionPreference = 'Continue'
        $raw = @(& $Executable @Arguments 2>&1)
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousPreference
        Set-Location -LiteralPath $previousLocation
        $timer.Stop()
    }
    $output = @($raw | ForEach-Object { Convert-NativeLine $_ })
    foreach ($line in $output) { Write-Host $line }
    $text = if ($output.Count -eq 0) { '' } else { ($output -join "`n") + "`n" }
    $record = [ordered]@{
        name = $Name
        executable = $Executable
        arguments = $Arguments
        workingDirectory = $WorkingDirectory
        exitCode = $exitCode
        passed = $exitCode -eq 0
        elapsedMillis = $timer.ElapsedMilliseconds
        outputLineCount = $output.Count
        outputSha256 = Get-TextSha256 $text
        lastOutputLine = if ($output.Count -eq 0) { $null } else { [string] $output[-1] }
    }
    $steps[$Name] = $record
    Assert-True ($exitCode -eq 0) "$Name failed with exit code $exitCode"
    return $record
}

function Invoke-GitLines([string] $Repository, [string[]] $Arguments) {
    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $raw = @(& git -C $Repository @Arguments 2>&1)
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousPreference
    }
    Assert-True ($exitCode -eq 0) "Git query failed in $Repository"
    return @($raw | ForEach-Object { Convert-NativeLine $_ })
}

function Get-SourceIdentity([string] $Repository) {
    $head = (Invoke-GitLines $Repository @('rev-parse', 'HEAD') | Select-Object -Last 1).Trim().ToLowerInvariant()
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

function Read-ContractReport(
    [string] $Name,
    [string] $RelativePath,
    [string] $ExpectedRole,
    [object] $ExpectedPluginIdentity,
    [object] $ExpectedHostIdentity
) {
    $path = [IO.Path]::GetFullPath((Join-Path $repoRoot $RelativePath))
    Assert-True (Test-Path -LiteralPath $path -PathType Leaf) "$Name report is missing"
    $json = Get-Content -Raw -LiteralPath $path | ConvertFrom-Json -Depth 40
    Assert-True ([string] $json.status -ceq 'PASS') "$Name report did not pass"
    Assert-True ([string] $json.phaseStatus -ceq 'PARTIAL') "$Name report exceeded its E2 boundary"
    Assert-True ([string] $json.reportRole -ceq $ExpectedRole) "$Name report role differs"
    Assert-True ($json.claims.binderExecuted -eq $false -and $json.claims.deviceVerified -eq $false) "$Name report contains a device claim"
    Assert-True ($json.claims.productionEvidence -eq $false -and $json.claims.published -eq $false -and $json.claims.releaseAuthorized -eq $false) "$Name report contains a release claim"
    Assert-True ([string] $json.sourceIdentity.plugin.commit -ceq [string] $ExpectedPluginIdentity.commit) "$Name Plugin commit differs"
    Assert-True ([string] $json.sourceIdentity.host.commit -ceq [string] $ExpectedHostIdentity.commit) "$Name Host commit differs"
    Assert-True ([IO.Path]::GetFullPath([string] $json.sourceIdentity.plugin.repository).Equals($repoRoot, [StringComparison]::OrdinalIgnoreCase)) "$Name Plugin repository differs"
    Assert-True ([IO.Path]::GetFullPath([string] $json.sourceIdentity.host.repository).Equals($resolvedHostRepository, [StringComparison]::OrdinalIgnoreCase)) "$Name Host repository differs"
    return [ordered]@{
        path = $path
        sizeBytes = [long] (Get-Item -LiteralPath $path).Length
        sha256 = Get-FileSha256 $path
        status = 'PASS'
        phaseStatus = 'PARTIAL'
        reportRole = $ExpectedRole
    }
}

try {
    $pluginGradle = Join-Path $repoRoot 'gradlew.bat'
    $hostGradle = Join-Path $resolvedHostRepository 'gradlew.bat'
    Assert-True (Test-Path -LiteralPath $pluginGradle -PathType Leaf) 'Plugin Gradle wrapper is missing'
    Assert-True (Test-Path -LiteralPath $hostGradle -PathType Leaf) 'Host Gradle wrapper is missing'
    Assert-True (Test-Path -LiteralPath (Join-Path $resolvedHostRepository 'plugin-api/python-runtime-api') -PathType Container) 'Host python-runtime-api module is missing'
    $currentPowerShell = (Get-Process -Id $PID).Path
    Assert-True (Test-Path -LiteralPath $currentPowerShell -PathType Leaf) 'Current PowerShell executable is unavailable'

    $version = Invoke-RecordedStep `
        -Name 'localPythonVersion' `
        -Executable $PythonExecutable `
        -Arguments @('-B', '-c', 'import platform; print(platform.python_version())') `
        -WorkingDirectory $repoRoot
    $pythonVersion = [string] $version.lastOutputLine

    foreach ($definition in @(
        [pscustomobject]@{
            Name = 'moduleIoContract'
            Script = 'tools/verify-u1-r2-module-io.ps1'
            Report = 'build/reports/python/u1/r2-module-io-contract.json'
            Role = 'CURRENT_TREE_R2_MODULE_AND_OUTPUT_PARTIAL_FUNCTIONAL_GATE'
        },
        [pscustomobject]@{
            Name = 'interactiveInputContract'
            Script = 'tools/verify-u1-r2-interactive-input.ps1'
            Report = 'build/reports/python/u1/r2-interactive-input-contract.json'
            Role = 'CURRENT_TREE_R2_INTERACTIVE_INPUT_PARTIAL_FUNCTIONAL_GATE'
        },
        [pscustomobject]@{
            Name = 'structuredResultsContract'
            Script = 'tools/verify-u1-r2-structured-results.ps1'
            Report = 'build/reports/python/u1/r2-structured-results-contract.json'
            Role = 'CURRENT_TREE_R2_STRUCTURED_RESULTS_PARTIAL_FUNCTIONAL_GATE'
        }
    )) {
        $scriptPath = [IO.Path]::GetFullPath((Join-Path $repoRoot $definition.Script))
        Assert-True (Test-Path -LiteralPath $scriptPath -PathType Leaf) "$($definition.Name) verifier is missing"
        Invoke-RecordedStep `
            -Name $definition.Name `
            -Executable $currentPowerShell `
            -Arguments @(
                '-NoProfile',
                '-ExecutionPolicy', 'Bypass',
                '-File', $scriptPath,
                '-PythonExecutable', $PythonExecutable,
                '-HostRepository', $resolvedHostRepository
            ) `
            -WorkingDirectory $repoRoot | Out-Null
    }

    # The three E2 contract verifiers above already run the frozen, targeted
    # Host app tests for module/output, interactive input and structured
    # results. Keep this aggregate gate scoped to the Python API and R2
    # AndroidTest build: an unrelated Host feature's unit-test failure must not
    # silently redefine the R2 evidence contract.
    Invoke-RecordedStep `
        -Name 'hostPythonApiTests' `
        -Executable $hostGradle `
        -Arguments @(
            '--no-parallel',
            '--console=plain',
            ':plugin-api:python-runtime-api:test'
        ) `
        -WorkingDirectory $resolvedHostRepository | Out-Null

    Invoke-RecordedStep `
        -Name 'hostAndroidTestCompile' `
        -Executable $hostGradle `
        -Arguments @(
            '--no-parallel',
            '--console=plain',
            ':app:compileAppDebugAndroidTestKotlin'
        ) `
        -WorkingDirectory $resolvedHostRepository | Out-Null

    Invoke-RecordedStep `
        -Name 'hostAppPackage' `
        -Executable $hostGradle `
        -Arguments @(
            '--no-parallel',
            '--console=plain',
            ':app:assembleAppDebug'
        ) `
        -WorkingDirectory $resolvedHostRepository | Out-Null

    Invoke-RecordedStep `
        -Name 'hostAndroidTestPackage' `
        -Executable $hostGradle `
        -Arguments @(
            '--no-parallel',
            '--console=plain',
            ':app:assembleAppDebugAndroidTest'
        ) `
        -WorkingDirectory $resolvedHostRepository | Out-Null

    $pluginIdentity = Get-SourceIdentity $repoRoot
    $hostIdentity = Get-SourceIdentity $resolvedHostRepository
    $contracts.moduleIo = Read-ContractReport `
        'Module/output' `
        'build/reports/python/u1/r2-module-io-contract.json' `
        'CURRENT_TREE_R2_MODULE_AND_OUTPUT_PARTIAL_FUNCTIONAL_GATE' `
        $pluginIdentity `
        $hostIdentity
    $contracts.interactiveInput = Read-ContractReport `
        'Interactive input' `
        'build/reports/python/u1/r2-interactive-input-contract.json' `
        'CURRENT_TREE_R2_INTERACTIVE_INPUT_PARTIAL_FUNCTIONAL_GATE' `
        $pluginIdentity `
        $hostIdentity
    $contracts.structuredResults = Read-ContractReport `
        'Structured results' `
        'build/reports/python/u1/r2-structured-results-contract.json' `
        'CURRENT_TREE_R2_STRUCTURED_RESULTS_PARTIAL_FUNCTIONAL_GATE' `
        $pluginIdentity `
        $hostIdentity
} catch {
    $failureMessage = $_.Exception.Message
    if ($null -eq $pluginIdentity) { try { $pluginIdentity = Get-SourceIdentity $repoRoot } catch {} }
    if ($null -eq $hostIdentity) { try { $hostIdentity = Get-SourceIdentity $resolvedHostRepository } catch {} }
}

$passed = $null -eq $failureMessage
$contractStepsPassed =
    $steps.Contains('moduleIoContract') -and [bool] $steps['moduleIoContract'].passed -and
    $steps.Contains('interactiveInputContract') -and [bool] $steps['interactiveInputContract'].passed -and
    $steps.Contains('structuredResultsContract') -and [bool] $steps['structuredResultsContract'].passed
$hostPythonApiPassed = $steps.Contains('hostPythonApiTests') -and [bool] $steps['hostPythonApiTests'].passed
$hostAndroidTestCompiled = $steps.Contains('hostAndroidTestCompile') -and [bool] $steps['hostAndroidTestCompile'].passed
$hostAppPackaged = $steps.Contains('hostAppPackage') -and [bool] $steps['hostAppPackage'].passed
$hostAndroidTestPackaged = $steps.Contains('hostAndroidTestPackage') -and [bool] $steps['hostAndroidTestPackage'].passed
$report = [ordered]@{
    schema = 1
    track = 'U1'
    phase = 'R2'
    status = if ($passed) { 'PASS' } else { 'FAIL' }
    reportRole = 'CURRENT_TREE_R2_E3_FUNCTIONAL_GATE'
    startedAtUtc = $startedAtUtc.ToString('o')
    completedAtUtc = [DateTimeOffset]::UtcNow.ToString('o')
    evidenceLevels = @('PORTABLE_CPYTHON_ONLY', 'ANDROID_BUILD_ONLY', 'HOST_ANDROID_TEST_BUILD_ONLY')
    sourceIdentity = [ordered]@{
        plugin = $pluginIdentity
        host = $hostIdentity
    }
    scope = [ordered]@{
        portablePythonTests = $true
        pluginJvmTests = $true
        pluginDebugApk = $true
        hostRepository = $resolvedHostRepository
        hostPythonApiAndAppTests = $contractStepsPassed -and $hostPythonApiPassed
        hostCheckScope = 'PYTHON_API_AND_FROZEN_R2_APP_TARGETS_ONLY'
        hostFullAppSuiteExecuted = $false
        hostAndroidTestCompiled = $hostAndroidTestCompiled
        hostAppApkPackaged = $hostAppPackaged
        hostAndroidTestApkPackaged = $hostAndroidTestPackaged
        contracts = $contracts
    }
    localPython = [ordered]@{
        executable = $PythonExecutable
        version = $pythonVersion
        exactPackagedTargetVersion = $pythonVersion -ceq '3.13.9'
    }
    steps = $steps
    claims = [ordered]@{
        portableTestsPassed = $passed -and $contractStepsPassed
        androidCompiled = $passed -and $hostAndroidTestCompiled
        apkPackaged = $passed -and $hostAppPackaged -and $hostAndroidTestPackaged
        hostChecked = $passed -and $contractStepsPassed -and $hostPythonApiPassed
        binderExecuted = $false
        deviceVerified = $false
        productionEvidence = $false
        published = $false
        releaseAuthorized = $false
    }
    error = $failureMessage
}

$reportDirectory = Split-Path -Parent $reportPath
[void] [IO.Directory]::CreateDirectory($reportDirectory)
$temporaryPath = Join-Path $reportDirectory ('.' + [IO.Path]::GetFileName($reportPath) + '.' + [Guid]::NewGuid().ToString('N') + '.tmp')
try {
    [IO.File]::WriteAllText($temporaryPath, (($report | ConvertTo-Json -Depth 30) + "`n"), $utf8WithoutBom)
    Move-Item -LiteralPath $temporaryPath -Destination $reportPath -Force
} finally {
    if (Test-Path -LiteralPath $temporaryPath -PathType Leaf) { Remove-Item -LiteralPath $temporaryPath -Force }
}

if (-not $passed) {
    throw "U1-R2 E3 functional gate failed: $failureMessage; report=$reportRelative"
}

Write-Output 'U1_R2_E3_FUNCTIONAL_STATUS=PASS'
Write-Output "OUTPUT=$reportPath"
Write-Output "OUTPUT_SHA256=$(Get-FileSha256 $reportPath)"
Write-Output 'BINDER_EXECUTED=false'
Write-Output 'DEVICE_VERIFIED=false'
