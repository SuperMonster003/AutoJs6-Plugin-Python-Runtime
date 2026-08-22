param(
    [string]$PythonExecutable = 'python'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$repoRoot = Split-Path -Parent $PSScriptRoot
$fixtureRelative = 'tools/tests/fixtures/u1-r0-python-semantics-cases.json'
$contractRelative = 'docs/python/PYTHON_SEMANTICS_CONTRACT.md'
$roadmapRelative = 'docs/legacy/ROADMAP-u1-en.md'
$reportRelative = 'build/reports/python/u1/r0-python-usability-gate.json'
$fixturePath = Join-Path $repoRoot $fixtureRelative
$contractPath = Join-Path $repoRoot $contractRelative
$roadmapPath = Join-Path $repoRoot $roadmapRelative
$reportPath = Join-Path $repoRoot $reportRelative

function Assert-True([bool]$Condition, [string]$Message) {
    if (-not $Condition) {
        throw $Message
    }
}

function Read-RequiredText([string]$Path, [string]$Label) {
    Assert-True (Test-Path -LiteralPath $Path -PathType Leaf) "$Label is missing: $Path"
    $value = [IO.File]::ReadAllText($Path, [Text.Encoding]::UTF8)
    Assert-True (-not [string]::IsNullOrWhiteSpace($value)) "$Label is empty: $Path"
    return $value
}

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Invoke-CheckedNative([string]$Executable, [string[]]$Arguments, [string]$Label) {
    $previousErrorAction = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $output = @(& $Executable @Arguments 2>&1)
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorAction
    }
    foreach ($line in $output) {
        Write-Host ([string]$line)
    }
    Assert-True ($exitCode -eq 0) "$Label failed with exit code $exitCode"
    return @($output | ForEach-Object { [string]$_ })
}

$roadmap = Read-RequiredText $roadmapPath 'Roadmap'
$contract = Read-RequiredText $contractPath 'Python semantics contract'
$fixtureText = Read-RequiredText $fixturePath 'U1-R0 semantics fixture'
$manifest = $fixtureText | ConvertFrom-Json

Assert-True ([int]$manifest.schema -eq 1) 'Fixture schema must be 1'
Assert-True ([string]$manifest.track -ceq 'U1') 'Fixture track must be U1'
Assert-True ([string]$manifest.phase -ceq 'R0') 'Fixture phase must be R0'
Assert-True ([string]$manifest.targetRuntime.implementation -ceq 'CPython') 'Target implementation must be CPython'
Assert-True ([string]$manifest.targetRuntime.pythonVersion -ceq '3.13.9') 'Target Python must be 3.13.9'
Assert-True (
    [string]$manifest.targetRuntime.sourceEncodingTarget -ceq 'STRICT_UTF8_OPTIONAL_BOM'
) 'Target source encoding policy mismatch'

$boundary = $manifest.evidenceBoundary
Assert-True ([string]$boundary.level -ceq 'PORTABLE_CPYTHON_ONLY') 'Fixture evidence level mismatch'
foreach ($property in @('androidCompiled', 'binderExecuted', 'deviceVerified', 'published')) {
    Assert-True ($boundary.$property -eq $false) "Fixture evidenceBoundary.$property must be false"
}

$cases = @($manifest.cases)
Assert-True ($cases.Count -ge 10) 'Fixture must contain at least ten semantic cases'
$caseIds = @($cases | ForEach-Object { [string]$_.id })
Assert-True (@($caseIds | Where-Object { [string]::IsNullOrWhiteSpace($_) }).Count -eq 0) 'Fixture contains a blank case ID'
Assert-True (@($caseIds | Group-Object | Where-Object Count -ne 1).Count -eq 0) 'Fixture case IDs are not unique'

$allowedClaims = @('VERIFIED_PORTABLE', 'IMPLEMENTED_NOT_GATED', 'CONTRACT_GAP', 'UNSUPPORTED')
$allowedTargets = @('R1', 'R2', 'R3', 'R4', 'R5', 'R6')
$allowedExecutableKinds = @('SOURCE', 'PROJECT')
foreach ($case in $cases) {
    $identifier = [string]$case.id
    $claim = [string]$case.currentClaim
    $target = [string]$case.targetPhase
    $kind = [string]$case.execution.kind
    Assert-True ($claim -cin $allowedClaims) "Unsupported current claim in $identifier"
    Assert-True ($target -cin $allowedTargets) "Unsupported target phase in $identifier"
    Assert-True (-not [string]::IsNullOrWhiteSpace([string]$case.category)) "Missing category in $identifier"
    Assert-True (-not [string]::IsNullOrWhiteSpace([string]$case.rationale)) "Missing rationale in $identifier"
    if ($claim -ceq 'VERIFIED_PORTABLE') {
        Assert-True ($kind -cin $allowedExecutableKinds) "Portable case $identifier is not executable"
        Assert-True ($null -ne $case.expected) "Portable case $identifier has no expected result"
    }
    else {
        Assert-True ($kind -ceq 'NONE') "Non-portable case $identifier must use execution kind NONE"
        Assert-True ($null -eq $case.expected) "Non-portable case $identifier must not carry an executable result"
    }
}

$requiredCases = [ordered]@{
    'source.encoding.strict-utf8' = @('VERIFIED_PORTABLE', 'R1')
    'stdin.snapshot.input' = @('VERIFIED_PORTABLE', 'R1')
    'project.entry.module-relative-import' = @('VERIFIED_PORTABLE', 'R1')
    'package.third-party.offline-pack' = @('UNSUPPORTED', 'R3')
}
foreach ($entry in $requiredCases.GetEnumerator()) {
    $case = @($cases | Where-Object { [string]$_.id -ceq [string]$entry.Key })
    Assert-True ($case.Count -eq 1) "Required case is missing or duplicated: $($entry.Key)"
    Assert-True ([string]$case[0].currentClaim -ceq [string]$entry.Value[0]) "Current claim mismatch: $($entry.Key)"
    Assert-True ([string]$case[0].targetPhase -ceq [string]$entry.Value[1]) "Target phase mismatch: $($entry.Key)"
}

foreach ($stage in 0..6) {
    Assert-True ($roadmap -match "U1-R$stage") "Roadmap is missing U1-R$stage"
}
Assert-True ($roadmap -match 'Existing\s+RC receipts are historical') 'Historical RC boundary is missing'
Assert-True ($roadmap -match 'complete API 24-36 by ABI\s+matrix is not automatic') 'Risk-proportional matrix boundary is missing'
Assert-True ($roadmap -match 'production receipt') 'Production receipt boundary is missing'
Assert-True ($roadmap.Replace('\', '/') -match [regex]::Escape($fixtureRelative)) 'Roadmap does not name the fixture'
Assert-True ($roadmap.Replace('\', '/') -match [regex]::Escape($reportRelative)) 'Roadmap does not name the report'
Assert-True ($contract.Replace('\', '/') -match [regex]::Escape($fixtureRelative)) 'Contract does not name the fixture'
Assert-True ($contract.Replace('\', '/') -match [regex]::Escape($reportRelative)) 'Contract does not name the report'
Assert-True ($contract -match 'supportsStdinSnapshot=true') 'Contract does not describe current stdin truth'
Assert-True ($contract -match 'finite pre-supplied input') 'Contract does not distinguish snapshot from interactive input'
Assert-True ($contract -match 'standalone `.py` snapshot contains only that source') 'Standalone import boundary is missing'
Assert-True ($contract -match 'No import failure may trigger online pip') 'Import fail-closed boundary is missing'

$pythonVersionOutput = Invoke-CheckedNative $PythonExecutable @(
    '-B', '-c', 'import platform; print(platform.python_version())'
) 'Local Python version query'
$pythonVersion = ($pythonVersionOutput | Select-Object -Last 1).Trim()
Assert-True ($pythonVersion -match '^\d+\.\d+\.\d+') 'Local Python version output is malformed'

$testOutput = Invoke-CheckedNative $PythonExecutable @(
    '-B', '-m', 'unittest', 'tools.tests.test_u1_r0_python_usability_source', '-v'
) 'U1-R0 portable semantics test'
Assert-True (($testOutput -join "`n") -match 'OK') 'Portable test output does not contain the unittest OK sentinel'

$headOutput = Invoke-CheckedNative 'git' @('-C', $repoRoot, 'rev-parse', 'HEAD') 'Git HEAD query'
$head = ($headOutput | Select-Object -Last 1).Trim()
Assert-True ($head -match '^[0-9a-f]{40}$') 'Git HEAD is not a full commit ID'
$statusOutput = Invoke-CheckedNative 'git' @(
    '-C', $repoRoot, 'status', '--porcelain=v1', '--untracked-files=all'
) 'Git worktree query'
$changes = @($statusOutput | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

$claimCounts = [ordered]@{}
$categoryCounts = [ordered]@{}
foreach ($case in $cases) {
    $claim = [string]$case.currentClaim
    $category = [string]$case.category
    if (-not $claimCounts.Contains($claim)) { $claimCounts[$claim] = 0 }
    if (-not $categoryCounts.Contains($category)) { $categoryCounts[$category] = 0 }
    $claimCounts[$claim] = [int]$claimCounts[$claim] + 1
    $categoryCounts[$category] = [int]$categoryCounts[$category] + 1
}

$report = [ordered]@{
    schema = 1
    track = 'U1'
    phase = 'R0'
    status = 'PASS'
    reportRole = if ($changes.Count -eq 0) { 'CLEAN_TREE_DEVELOPMENT_GATE' } else { 'CURRENT_TREE_DEVELOPMENT_GATE' }
    generatedAtUtc = [DateTime]::UtcNow.ToString('o')
    evidenceLevels = @('SOURCE_STATIC_ONLY', 'PORTABLE_CPYTHON_ONLY')
    sourceIdentity = [ordered]@{
        commit = $head
        dirty = $changes.Count -ne 0
        changes = $changes
    }
    targetRuntime = [ordered]@{
        implementation = [string]$manifest.targetRuntime.implementation
        pythonVersion = [string]$manifest.targetRuntime.pythonVersion
        sourceEncodingTarget = [string]$manifest.targetRuntime.sourceEncodingTarget
    }
    localPython = [ordered]@{
        executable = $PythonExecutable
        version = $pythonVersion
        exactTargetVersion = $pythonVersion -ceq [string]$manifest.targetRuntime.pythonVersion
    }
    cases = [ordered]@{
        total = $cases.Count
        executablePortable = @($cases | Where-Object currentClaim -CEQ 'VERIFIED_PORTABLE').Count
        byCurrentClaim = $claimCounts
        byCategory = $categoryCounts
    }
    inputs = [ordered]@{
        roadmap = [ordered]@{ path = $roadmapRelative; sha256 = Get-Sha256 $roadmapPath }
        contract = [ordered]@{ path = $contractRelative; sha256 = Get-Sha256 $contractPath }
        fixture = [ordered]@{ path = $fixtureRelative; sha256 = Get-Sha256 $fixturePath }
        sourceTest = [ordered]@{
            path = 'tools/tests/test_u1_r0_python_usability_source.py'
            sha256 = Get-Sha256 (Join-Path $repoRoot 'tools/tests/test_u1_r0_python_usability_source.py')
        }
    }
    claims = [ordered]@{
        sourceStaticVerified = $true
        portableBootstrapVerified = $true
        androidCompiled = $false
        apkPackaged = $false
        binderExecuted = $false
        deviceVerified = $false
        published = $false
        releaseAuthorized = $false
    }
}

$reportDirectory = Split-Path -Parent $reportPath
[IO.Directory]::CreateDirectory($reportDirectory) | Out-Null
$temporaryPath = "$reportPath.tmp"
$utf8NoBom = New-Object Text.UTF8Encoding($false)
[IO.File]::WriteAllText(
    $temporaryPath,
    (($report | ConvertTo-Json -Depth 12) + "`n"),
    $utf8NoBom
)
Move-Item -LiteralPath $temporaryPath -Destination $reportPath -Force

Write-Host (
    "U1-R0 Python usability gate passed: cases=$($cases.Count) " +
    "portable=$(@($cases | Where-Object currentClaim -CEQ 'VERIFIED_PORTABLE').Count) " +
    "python=$pythonVersion dirty=$($changes.Count -ne 0) report=$reportRelative"
)
