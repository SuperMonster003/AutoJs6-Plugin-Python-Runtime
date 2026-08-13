param(
    [string]$PythonExecutable = 'python',
    [string]$HostRepository
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$repoRoot = Split-Path -Parent $PSScriptRoot
$reportRelative = 'build/reports/python/u1/r1-core-semantics-gate.json'
$reportPath = Join-Path $repoRoot $reportRelative
$steps = [ordered]@{}
$failureMessage = $null
$startedAtUtc = [DateTime]::UtcNow

function Assert-True([bool]$Condition, [string]$Message) {
    if (-not $Condition) {
        throw $Message
    }
}

function Get-TextSha256([string]$Text) {
    $bytes = [Text.Encoding]::UTF8.GetBytes($Text)
    $algorithm = [Security.Cryptography.SHA256]::Create()
    try {
        $digest = $algorithm.ComputeHash($bytes)
        return -join ($digest | ForEach-Object { $_.ToString('x2') })
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
    foreach ($line in $output) {
        Write-Host $line
    }
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
    Assert-True ($exitCode -eq 0) "Git query failed in $Repository"
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
$pythonVersion = $null

try {
    $pluginGradle = Join-Path $repoRoot 'gradlew.bat'
    Assert-True (Test-Path -LiteralPath $pluginGradle -PathType Leaf) 'Plugin Gradle wrapper is missing'

    if (-not [string]::IsNullOrWhiteSpace($HostRepository)) {
        $resolvedHostRepository = (Resolve-Path -LiteralPath $HostRepository).Path
        Assert-True (
            (Test-Path -LiteralPath (Join-Path $resolvedHostRepository 'gradlew.bat') -PathType Leaf)
        ) 'Host Gradle wrapper is missing'
        Assert-True (
            (Test-Path -LiteralPath (Join-Path $resolvedHostRepository 'plugin-api/python-runtime-api') -PathType Container)
        ) 'Host python-runtime-api module is missing'
    }

    $versionStep = Invoke-RecordedStep `
        'localPythonVersion' `
        $PythonExecutable `
        @('-B', '-c', 'import platform; print(platform.python_version())') `
        $repoRoot
    $pythonVersion = [string]$versionStep.lastOutputLine

    Invoke-RecordedStep `
        'portablePythonTests' `
        $PythonExecutable `
        @('-B', '-m', 'unittest', 'discover', '-s', 'tools/tests', '-p', 'test_*.py', '-v') `
        $repoRoot | Out-Null

    Invoke-RecordedStep `
        'pluginAndroidBuild' `
        $pluginGradle `
        @('--console=plain', ':app:testDebugUnitTest', ':app:assembleDebug') `
        $repoRoot | Out-Null

    if ($null -ne $resolvedHostRepository) {
        Invoke-RecordedStep `
            'hostApiAndAppBuild' `
            (Join-Path $resolvedHostRepository 'gradlew.bat') `
            @(
                '--console=plain',
                ':plugin-api:python-runtime-api:test',
                ':app:testAppDebugUnitTest',
                ':app:compileAppDebugKotlin'
            ) `
            $resolvedHostRepository | Out-Null
    }

    $pluginIdentity = Get-SourceIdentity $repoRoot
    if ($null -ne $resolvedHostRepository) {
        $hostIdentity = Get-SourceIdentity $resolvedHostRepository
    }
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

$passed = $null -eq $failureMessage
$report = [ordered]@{
    schema = 1
    track = 'U1'
    phase = 'R1'
    status = if ($passed) { 'PASS' } else { 'FAIL' }
    reportRole = 'CURRENT_TREE_FUNCTIONAL_GATE'
    startedAtUtc = $startedAtUtc.ToString('o')
    completedAtUtc = [DateTime]::UtcNow.ToString('o')
    evidenceLevels = @('PORTABLE_CPYTHON_ONLY', 'ANDROID_BUILD_ONLY')
    sourceIdentity = [ordered]@{
        plugin = $pluginIdentity
        host = $hostIdentity
    }
    scope = [ordered]@{
        portablePythonTests = $true
        pluginJvmTests = $true
        pluginDebugApk = $true
        hostRequested = $null -ne $resolvedHostRepository
        hostRepository = $resolvedHostRepository
        hostApiAndAppBuild = $steps.Contains('hostApiAndAppBuild')
    }
    localPython = [ordered]@{
        executable = $PythonExecutable
        version = $pythonVersion
        exactPackagedTargetVersion = $pythonVersion -ceq '3.13.9'
    }
    steps = $steps
    claims = [ordered]@{
        portableTestsPassed = $passed -and $steps.Contains('portablePythonTests')
        androidCompiled = $passed -and $steps.Contains('pluginAndroidBuild')
        apkPackaged = $passed -and $steps.Contains('pluginAndroidBuild')
        hostChecked = $passed -and $steps.Contains('hostApiAndAppBuild')
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
    throw "U1-R1 core semantics gate failed: $failureMessage; report=$reportRelative"
}

Write-Host (
    "U1-R1 core semantics gate passed: portable=true androidBuild=true " +
    "host=$($null -ne $resolvedHostRepository) device=false report=$reportRelative"
)
