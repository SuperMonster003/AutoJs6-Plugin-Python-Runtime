[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path

function Assert-True {
    param(
        [Parameter(Mandatory = $true)][bool]$Condition,
        [Parameter(Mandatory = $true)][string]$Message
    )
    if (-not $Condition) {
        throw $Message
    }
}

function Read-RequiredText {
    param([Parameter(Mandatory = $true)][string]$RelativePath)
    $path = Join-Path $repoRoot $RelativePath
    Assert-True (Test-Path -LiteralPath $path -PathType Leaf) "Missing required file: $RelativePath"
    return Get-Content -LiteralPath $path -Raw
}

function Read-Lock {
    param([Parameter(Mandatory = $true)][string]$RelativePath)
    $text = Read-RequiredText $RelativePath
    $data = @{}
    foreach ($line in ($text -split "`r?`n")) {
        $trimmed = $line.Trim()
        if ($trimmed.Length -eq 0 -or $trimmed.StartsWith('#')) { continue }
        $parts = $trimmed.Split('=', 2)
        Assert-True ($parts.Count -eq 2) "Malformed lock line in ${RelativePath}: $line"
        $key = $parts[0].Trim()
        Assert-True ($key.Length -gt 0) "Empty lock key in ${RelativePath}: $line"
        Assert-True (-not $data.ContainsKey($key)) "Duplicate lock key in ${RelativePath}: $key"
        $data[$key] = $parts[1].Trim()
    }
    return $data
}

function Get-TextSha256 {
    param([Parameter(Mandatory = $true)][string]$Text)
    $algorithm = [System.Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
        return (($algorithm.ComputeHash($bytes) | ForEach-Object { $_.ToString('x2') }) -join '')
    }
    finally {
        $algorithm.Dispose()
    }
}

function Test-RuntimeLockBootstrapAdmission {
    param(
        [AllowNull()][string]$PropertyValue,
        [Parameter(Mandatory = $true)][AllowEmptyCollection()][string[]]$Tasks,
        [Parameter(Mandatory = $true)][bool]$WriteLocks,
        [Parameter(Mandatory = $true)][bool]$HasUpdatedLocks,
        [Parameter(Mandatory = $true)][AllowEmptyCollection()][string[]]$VerificationAlgorithms,
        [Parameter(Mandatory = $true)][AllowEmptyCollection()][string[]]$ExcludedTasks,
        [Parameter(Mandatory = $true)][bool]$DryRun
    )
    $allowedTasks = @(':app:assembleDebug', ':app:lintDebug', ':app:testDebugUnitTest')
    $hasExactTasks = $Tasks.Count -eq $allowedTasks.Count -and
        (($Tasks | Sort-Object) -join "`n") -ceq (($allowedTasks | Sort-Object) -join "`n")
    return $PropertyValue -ceq 'true' -and
        $hasExactTasks -and
        $WriteLocks -and
        -not $HasUpdatedLocks -and
        $VerificationAlgorithms.Count -eq 1 -and
        $VerificationAlgorithms[0] -ceq 'sha256' -and
        $ExcludedTasks.Count -eq 0 -and
        -not $DryRun
}

function Assert-RuntimeArtifactInventory {
    param([Parameter(Mandatory = $true)][hashtable]$Lock)

    foreach ($key in @('runtime.artifacts.state', 'runtime.artifacts.count', 'runtime.artifacts.inventory.sha256')) {
        Assert-True ($Lock.ContainsKey($key)) "Missing runtime inventory lock value: $key"
    }
    $state = $Lock['runtime.artifacts.state']
    $count = 0
    Assert-True ([int]::TryParse($Lock['runtime.artifacts.count'], [ref]$count)) 'runtime.artifacts.count must be an integer'
    $inventorySha256 = $Lock['runtime.artifacts.inventory.sha256']
    $artifactNamespaceKeys = @($Lock.Keys | Where-Object { $_.StartsWith('runtime.artifact.') })
    Assert-True (@($artifactNamespaceKeys | Where-Object {
        $_ -notmatch '^runtime\.artifact\.\d{3}\.(coordinate|file|sha256)$'
    }).Count -eq 0) 'Runtime artifact inventory contains an unsupported key'
    $declaredArtifactKeys = $artifactNamespaceKeys

    if ($state -eq 'DEFERRED') {
        Assert-True ($count -eq 0) 'DEFERRED runtime inventory must have zero artifacts'
        Assert-True ($inventorySha256 -eq 'DEFERRED') 'DEFERRED runtime inventory must retain its explicit marker'
        Assert-True ($declaredArtifactKeys.Count -eq 0) 'DEFERRED runtime inventory must not contain candidate artifacts'
        return $state
    }

    Assert-True ($state -eq 'RESOLVED') "Unsupported runtime.artifacts.state: $state"
    Assert-True ($count -gt 0) 'RESOLVED runtime inventory must contain at least one artifact'
    Assert-True ($inventorySha256 -match '^[0-9a-f]{64}$') 'RESOLVED runtime inventory requires a lowercase SHA-256'
    $expectedArtifactKeys = [System.Collections.Generic.List[string]]::new()
    $artifactIdentities = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
    $canonicalLines = [System.Collections.Generic.List[string]]::new()
    for ($index = 0; $index -lt $count; $index++) {
        $ordinal = $index.ToString('000')
        $prefix = "runtime.artifact.$ordinal"
        $coordinateKey = "$prefix.coordinate"
        $fileKey = "$prefix.file"
        $sha256Key = "$prefix.sha256"
        foreach ($key in @($coordinateKey, $fileKey, $sha256Key)) {
            $expectedArtifactKeys.Add($key)
            Assert-True ($Lock.ContainsKey($key)) "Missing runtime artifact value: $key"
        }
        $coordinate = $Lock[$coordinateKey]
        $fileName = $Lock[$fileKey]
        $sha256 = $Lock[$sha256Key]
        Assert-True ($coordinate.Length -gt 0 -and $coordinate -notmatch '[\|\r\n]') "Invalid runtime artifact coordinate at $ordinal"
        Assert-True ($fileName.Length -gt 0 -and $fileName -notmatch '[/\\]' -and [IO.Path]::GetFileName($fileName) -eq $fileName) "Runtime artifact file must be a basename at $ordinal"
        Assert-True ($sha256 -match '^[0-9a-f]{64}$') "Runtime artifact SHA-256 is invalid at $ordinal"
        Assert-True ($artifactIdentities.Add("$coordinate|$fileName")) "Duplicate runtime artifact identity at $ordinal"
        $canonicalLines.Add("$ordinal|$coordinate|$fileName|$sha256")
    }
    $actualKeys = ($declaredArtifactKeys | Sort-Object) -join "`n"
    $expectedKeys = ($expectedArtifactKeys | Sort-Object) -join "`n"
    Assert-True ($actualKeys -ceq $expectedKeys) 'Runtime artifact inventory contains missing, extra, or non-contiguous entries'
    $canonicalInventory = ($canonicalLines -join "`n") + "`n"
    Assert-True ((Get-TextSha256 $canonicalInventory) -ceq $inventorySha256) 'Runtime artifact canonical inventory SHA-256 mismatch'
    return $state
}

$settings = Read-RequiredText 'settings.gradle.kts'
$rootBuild = Read-RequiredText 'build.gradle.kts'
$appBuild = Read-RequiredText 'app/build.gradle.kts'
$ordinaryGradleLock = Read-RequiredText 'app/gradle.lockfile'
$manifest = Read-RequiredText 'app/src/main/AndroidManifest.xml'
$roadmap = Read-RequiredText 'ROADMAP.md'
$versionProperties = Read-RequiredText 'version.properties'
$wrapperProperties = Read-RequiredText 'gradle/wrapper/gradle-wrapper.properties'
$metadataSource = Read-RequiredText 'app/src/main/java/io/github/supermonster003/autojs6/plugin/python/runtime/PythonRuntimeMetadata.kt'
$serviceSource = Read-RequiredText 'app/src/main/java/io/github/supermonster003/autojs6/plugin/python/runtime/service/PythonRuntimePluginService.kt'
$sessionSource = Read-RequiredText 'app/src/main/java/io/github/supermonster003/autojs6/plugin/python/runtime/service/PythonExecutionSession.kt'
$callerVerifierSource = Read-RequiredText 'app/src/main/java/io/github/supermonster003/autojs6/plugin/python/runtime/security/HostCallerVerifier.kt'
$ownedPfdSource = Read-RequiredText 'app/src/main/java/io/github/supermonster003/autojs6/plugin/python/runtime/transport/OwnedParcelFileDescriptors.kt'
$sourceSnapshotSource = Read-RequiredText 'app/src/main/java/io/github/supermonster003/autojs6/plugin/python/runtime/transport/SourceSnapshot.kt'
$bootstrapSource = Read-RequiredText 'app/src/main/python/autojs6_runtime/bootstrap.py'
$bootstrapTest = Read-RequiredText 'tools/tests/test_bootstrap.py'
$deferredDevicePlan = Read-RequiredText 'tools/device/deferred-device-plan-v1.json'
$deferredDeviceVerifier = Read-RequiredText 'tools/device/verify_deferred_device_plan.py'
$deferredDeviceTest = Read-RequiredText 'tools/tests/test_deferred_device_plan.py'
$runtimeInventoryCandidate = Read-RequiredText 'tools/runtime_lock_inventory_candidate.py'
$runtimeInventoryCandidateTest = Read-RequiredText 'tools/tests/test_runtime_lock_inventory_candidate.py'
$readme = Read-RequiredText 'README.md'
$runtimeAdr = Read-RequiredText 'docs/adr/0001-python-runtime-selection.md'
$lockWorkflow = Read-RequiredText 'locks/README.md'
$wrapperLock = Read-Lock 'locks/gradle-wrapper.lock'
$runtimeLock = Read-Lock 'locks/python-runtime.lock'
$hostLock = Read-Lock 'locks/host-api-aars.lock'

Assert-True ($settings -match 'rootProject\.name\s*=\s*"autojs6-plugin-python-runtime"') 'Root project identity drifted'
Assert-True ($rootBuild -match 'id\("com\.chaquo\.python"\)\s+version\s+"17\.0\.0"\s+apply false') 'Chaquopy plugin is not pinned to 17.0.0'
Assert-True ($rootBuild -notmatch '(?i)jitpack|aliyun|jcenter') 'Unapproved dependency repository is configured'
Assert-True ($appBuild -match 'globalApplicationId\s*=\s*"io\.github\.supermonster003\.autojs6\.plugin\.python\.runtime"') 'Application ID drifted'
Assert-True ($appBuild -match 'compileSdk\s*=\s*36') 'compileSdk must be 36'
Assert-True ($appBuild -match 'minSdk\s*=\s*24') 'minSdk must be 24'
Assert-True ($appBuild -match 'targetSdk\s*=\s*36') 'targetSdk must be 36'
Assert-True ($appBuild -match 'version\s*=\s*"3\.13"') 'Python line must be 3.13'
Assert-True ($versionProperties -match 'OVERRIDDEN_ANDROID_GRADLE_PLUGIN_VERSION=NONE') 'AGP override must remain disabled so platform compatibility selection stays active'
Assert-True ($settings -match 'overriddenAgpVersion\s*\?:\s*"auto:agp"') 'AGP classpath does not retain the automatic selection path'
Assert-True ($settings -match '"2026\.2"\s+to\s+"9\.1\.0"') 'IntelliJ IDEA 2026.2 must select its supported AGP 9.1.0 baseline'
Assert-True ($wrapperProperties -match 'distributionSha256Sum=553c78f50dafcd54d65b9a444649057857469edf836431389695608536d6b746') 'Gradle wrapper SHA-256 is missing or drifted'
Assert-True ($wrapperProperties -match 'distributionUrl=https\\://services\.gradle\.org/distributions/gradle-9\.5\.0-bin\.zip') 'Gradle wrapper distribution must remain pinned to 9.5.0'
Assert-True ($appBuild -match 'setOf\("arm64-v8a",\s*"x86_64"\)') 'ABI allowlist drifted'
Assert-True ($appBuild -match 'Regex\("\[0-9a-f\]\{64\}"\)') 'Gradle AAR hash validation is missing'
Assert-True ($appBuild -match 'Missing locked host API AAR') 'Gradle missing-AAR fail-closed check is absent'
Assert-True ($appBuild -match 'Runtime supply lock mismatch') 'Gradle does not consume the runtime supply lock'
Assert-True ($appBuild -match 'Runtime supply lock is DEFERRED') 'Gradle does not fail closed for the DEFERRED runtime inventory'
Assert-True ($appBuild -match 'runtimeArtifactsState\s*==\s*"RESOLVED"') 'Gradle does not require a resolved runtime inventory'
Assert-True ($appBuild -match 'Runtime artifact canonical inventory SHA-256 mismatch') 'Gradle canonical runtime inventory validation is absent'
Assert-True ($appBuild -match 'autojs\.python\.runtime\.lock\.bootstrap') 'Explicit runtime lock bootstrap property is absent'
Assert-True ($appBuild -match 'runtimeLockBootstrapRequestedTasks\.size\s*==\s*runtimeLockBootstrapAllowedTasks\.size') 'Runtime lock bootstrap does not require the exact task count'
Assert-True ($appBuild -match 'runtimeLockBootstrapRequestedTasks\.toSet\(\)\s*==\s*runtimeLockBootstrapAllowedTasks') 'Runtime lock bootstrap does not require the exact task set'
Assert-True ($appBuild -match 'startParameter\.isWriteDependencyLocks') 'Runtime lock bootstrap does not require --write-locks'
Assert-True ($appBuild -match 'lockedDependenciesToUpdate\.isEmpty\(\)') 'Runtime lock bootstrap does not reject --update-locks'
Assert-True ($appBuild -match 'writeDependencyVerifications\s*==\s*listOf\("sha256"\)') 'Runtime lock bootstrap does not require exact SHA-256 verification metadata mode'
Assert-True ($appBuild -match 'excludedTaskNames\.isEmpty\(\)') 'Runtime lock bootstrap does not reject excluded tasks'
Assert-True ($appBuild -match '!gradle\.startParameter\.isDryRun') 'Runtime lock bootstrap does not reject dry-run mode'
Assert-True ($appBuild -match 'runtimeArtifactsState\s*==\s*"RESOLVED"\s*\|\|\s*runtimeLockBootstrapAdmitted') 'DEFERRED exception is not bound to the complete bootstrap admission predicate'
$bootstrapTaskBlock = [regex]::Match($appBuild, '(?s)val runtimeLockBootstrapAllowedTasks\s*=\s*setOf\((?<body>.*?)\)')
Assert-True ($bootstrapTaskBlock.Success) 'Runtime lock bootstrap allowed-task block is absent'
$bootstrapTaskBody = $bootstrapTaskBlock.Groups['body'].Value
$declaredBootstrapTasks = @([regex]::Matches($bootstrapTaskBody, '"(?<task>:[^"]+)"') | ForEach-Object { $_.Groups['task'].Value })
Assert-True ($declaredBootstrapTasks.Count -eq 3) 'Runtime lock bootstrap must declare exactly three tasks'
Assert-True ((($declaredBootstrapTasks | Sort-Object) -join "`n") -ceq ((@(':app:assembleDebug', ':app:lintDebug', ':app:testDebugUnitTest') | Sort-Object) -join "`n")) 'Runtime lock bootstrap task allowlist drifted'
Assert-True ($bootstrapTaskBody -notmatch '(?i)release|androidTest|connected|device|install|bundle') 'Runtime lock bootstrap admits a release or device task'
Assert-True ($appBuild -match 'Gradle wrapper provenance is BLOCKED') 'Gradle wrapper provenance does not fail closed'
$obsoleteRuntimeMarker = @('UNRESOLVED', 'AFTER', 'DEPENDENCY', 'RESOLUTION') -join '_'
Assert-True ($appBuild -notmatch [regex]::Escape($obsoleteRuntimeMarker)) 'Gradle still hard-codes the obsolete unresolved marker'
Assert-True ($appBuild -match 'lockMode\s*=\s*LockMode\.STRICT') 'Strict Gradle dependency locking is absent'
Assert-True ($appBuild -match 'System\.getProperty\("idea\.sync\.active"\)\.toBoolean\(\)') 'IntelliJ dependency-model import detection is absent'
Assert-True ($appBuild -match '!isIdeaSync\s*&&\s*\(name\.endsWith\("CompileClasspath"\)\s*\|\|\s*name\.endsWith\("RuntimeClasspath"\)\)') 'Dependency locking is not scoped to non-IDE application and test variant classpaths'
Assert-True ($appBuild -match 'resolutionStrategy\.activateDependencyLocking\(\)') 'Scoped dependency-lock activation is absent'
Assert-True ($appBuild -notmatch 'lockAllConfigurations\(\)') 'AGP-owned tool configurations must not be pinned across auto-selected AGP versions'
Assert-True ($ordinaryGradleLock -match 'releaseCompileClasspath' -and $ordinaryGradleLock -match 'releaseRuntimeClasspath') 'Ordinary dependency lock is missing release variant coverage'
Assert-True ($ordinaryGradleLock -notmatch 'androidLintTool|unified-test-platform|kotlinCompilerClasspath|kotlinBuildToolsApiClasspath|aapt2-proto') 'Ordinary dependency lock contains an AGP-owned tool configuration or artifact'
Assert-True ($ordinaryGradleLock -notmatch 'com\.chaquo\.python') 'Ordinary dependency lock must not be treated as the Chaquopy runtime inventory'
Assert-True ($appBuild -notmatch '(?m)^\s*pip\s*\{') 'Online or build-time pip configuration is forbidden in R2'

Assert-True ($manifest -match 'android:process=":python_runtime"') 'Runtime process identity drifted'
Assert-True ($manifest -match 'android:name="\.service\.PythonRuntimePluginService"') 'Runtime service class identity drifted'
Assert-True ($manifest -match 'android:name="org\.autojs\.plugin\.python\.RUNTIME"') 'Binder action drifted'
Assert-True ($manifest -match 'android:value="org\.autojs\.python\.runtime\.cpython"') 'Provider ID drifted'
Assert-True ($manifest -match 'android:permission="org\.autojs\.permission\.PLUGIN"') 'Signature permission guard is missing'
Assert-True ($manifest -notmatch '<uses-permission\b') 'The untrusted runtime APK must request no Android permissions'
Assert-True ($manifest -notmatch 'android\.permission\.INTERNET') 'Internet permission is forbidden in R2'
Assert-True ($manifest -notmatch 'android:sharedUserId') 'A shared Android UID is forbidden'
Assert-True ($manifest -notmatch 'com\.chaquo\.python\.android\.PyApplication') 'CPython must not start in the application/main process'

Assert-True ($metadataSource -match 'supportsWorkspaceArchive\s*=\s*true') 'Verified project workspace transport must stay enabled'
Assert-True ($metadataSource -match 'maxWorkspaceArchiveBytes\s*=\s*16L\s*\*\s*1024L\s*\*\s*1024L') 'Workspace archive limit drifted'
Assert-True ($metadataSource -match 'maxWorkspaceEntries\s*=\s*1024') 'Workspace entry-count limit drifted'
Assert-True ($metadataSource -match 'maxWorkspaceUncompressedBytes\s*=\s*32L\s*\*\s*1024L\s*\*\s*1024L') 'Workspace expansion limit drifted'
Assert-True ($metadataSource -match 'supportsStdinSnapshot\s*=\s*true') 'bounded stdin snapshot capability must be enabled'
Assert-True ($metadataSource -match 'maxStdinBytes\s*=\s*1L\s*\*\s*1024L\s*\*\s*1024L') 'stdin snapshot limit must remain 1 MiB'
Assert-True ($metadataSource -match 'supportsCooperativeCancellation\s*=\s*false') 'Cooperative cancellation must not be claimed'
Assert-True ($metadataSource -match 'PythonCancellationMode\.PROCESS_RESTART_ONLY') 'Cancellation mode must remain process restart only'
Assert-True ($serviceSource -match 'callerVerifier\.enforceAllowedCaller\(\)') 'Provider Binder entry verification is absent'
Assert-True ($sessionSource -match 'callerVerifier\.enforceSessionOwner\(ownerUid\)') 'Session owner revalidation is absent'
Assert-True ($sessionSource -match 'SourceSnapshot\.materialize') 'SOURCE snapshot validation path is absent'
$publishStartedCallIndex = $sessionSource.IndexOf('if (!publishStartedAndWait() || isStopped()) return', [StringComparison]::Ordinal)
$runExecutionIndex = $sessionSource.IndexOf('private fun runExecution()', [StringComparison]::Ordinal)
$stageInputsCallIndex = $sessionSource.IndexOf('val stagedInputs = stageInputs() ?: return', [StringComparison]::Ordinal)
$stageInputsDefinitionIndex = $sessionSource.IndexOf('private fun stageInputs()', [StringComparison]::Ordinal)
$sourceMaterializeIndex = $sessionSource.IndexOf('SourceSnapshot.materialize', [StringComparison]::Ordinal)
$publishStartedDefinitionIndex = $sessionSource.IndexOf('private fun publishStartedAndWait()', [StringComparison]::Ordinal)
Assert-True ($runExecutionIndex -ge 0 -and $stageInputsCallIndex -gt $runExecutionIndex -and $publishStartedCallIndex -gt $stageInputsCallIndex) 'runExecution must stage all inputs before publishing onStarted'
Assert-True ($stageInputsDefinitionIndex -ge 0 -and $sourceMaterializeIndex -gt $stageInputsDefinitionIndex) 'stageInputs must validate the SOURCE snapshot'
Assert-True ($runExecutionIndex -ge 0 -and $publishStartedDefinitionIndex -gt $runExecutionIndex) 'Deferred onStarted publication path is absent'
$startMethodIndex = $sessionSource.IndexOf('override fun start()', [StringComparison]::Ordinal)
Assert-True ($startMethodIndex -ge 0 -and $runExecutionIndex -gt $startMethodIndex) 'Session start/runExecution structure drifted'
$startMethodText = $sessionSource.Substring($startMethodIndex, $runExecutionIndex - $startMethodIndex)
Assert-True ($startMethodText -notmatch 'executionCallback\.onStarted') 'start() must not publish onStarted before SOURCE staging'
Assert-True ($sessionSource -match 'executionCallback\.onStarted\(payload\)') 'Deferred onStarted callback dispatch is absent'
Assert-True ($sessionSource -match 'publishStartedAndWait\(\)\s*\|\|\s*isStopped\(\)') 'Runtime preparation is not guarded after deferred onStarted publication'
Assert-True ($sessionSource -match 'retirement\.retireNow\(\)') 'Hard process retirement path is absent'
Assert-True ($callerVerifierSource -match 'PackageManager\.GET_SIGNATURES') 'API 24-27 signer verification branch is absent'
Assert-True ($callerVerifierSource -match 'PackageManager\.GET_SIGNING_CERTIFICATES') 'Modern signer verification branch is absent'
Assert-True ($callerVerifierSource -match 'providerSigners\s*!=\s*hostSigners') 'Exact current signer-set comparison is absent'
Assert-True ($ownedPfdSource -match 'fun takeReceiverCopies\(') 'Complete Binder receiver-PFD ownership transfer is absent'
Assert-True ($ownedPfdSource -notmatch 'ParcelFileDescriptor\.dup') 'Raw data-FD duplication would discard reliable-pipe errors'
Assert-True ($sourceSnapshotSource -match 'descriptor\.canDetectErrors\(\)') 'Reliable-pipe error detection is absent'
Assert-True ($sourceSnapshotSource -match 'descriptor\.checkError\(\)') 'Reliable-pipe producer error check is absent'
Assert-True ($bootstrapSource -match 'def run_source\(') 'Python bootstrap entry point is absent'
Assert-True ($bootstrapSource -notmatch '(?m)^\s*(?:import|from)\s+(?:urllib|requests|httpx|socket)\b') 'Bootstrap must not contain network clients'
Assert-True ($bootstrapTest -match 'class BootstrapTest\(') 'Local bootstrap semantic tests are absent'
Assert-True ($deferredDevicePlan -match '"status"\s*:\s*"DEFERRED"') 'Device plan must remain deferred'
Assert-True ($deferredDevicePlan -match '"executionAuthorized"\s*:\s*false') 'Device execution must remain unauthorized'
Assert-True ($deferredDevicePlan -match '"QV710AF65F"') 'Protected soak serial is absent from the device plan'
Assert-True ($deferredDevicePlan -match '"confirmed"\s*:\s*false') 'Device plan must not claim soak completion'
Assert-True ($deferredDevicePlan -match '"currentClaim"\s*:\s*"NOT_RUN"') 'Device plan must not contain acceptance evidence'
Assert-True ($deferredDeviceVerifier -match 'ADB_PREFIX\s*=\s*\["adb",\s*"-s",\s*SERIAL_PLACEHOLDER\]') 'Future ADB templates are not exact-serial scoped'
Assert-True ($deferredDeviceVerifier -match 'def validate_plan\(') 'Deferred device plan validator is absent'
Assert-True ($deferredDeviceVerifier -notmatch '(?m)^\s*(?:import|from)\s+subprocess\b') 'Deferred validator must not invoke subprocesses'
Assert-True ($deferredDeviceVerifier -notmatch '(?i)os\.system|popen\(|create_subprocess|write_text\(') 'Deferred validator gained execution or write capability'
Assert-True ($deferredDeviceTest -match 'class DeferredDevicePlanTest\(') 'Deferred device contract tests are absent'
Assert-True ($runtimeInventoryCandidate -match 'CHAQUOPY_GROUP_PREFIX\s*=\s*"com\.chaquo\.python"') 'Runtime inventory candidate does not restrict Chaquopy coordinates'
Assert-True ($runtimeInventoryCandidate -match 'PYTHON_RUNTIME_VERSION\s*=\s*"3\.13\.9-0"') 'Runtime inventory candidate does not pin the exact CPython runtime version'
Assert-True ($runtimeInventoryCandidate -match 'SUPPORTED_ABIS\s*=\s*\("arm64-v8a",\s*"x86_64"\)') 'Runtime inventory candidate ABI contract drifted'
Assert-True ($runtimeInventoryCandidate -match 'EXPECTED_RUNTIME_ARTIFACTS\s*=') 'Exact plugin-managed runtime artifact contract is absent'
Assert-True (@([regex]::Matches($runtimeInventoryCandidate, '^\s*\(\s*$', [System.Text.RegularExpressions.RegexOptions]::Multiline)).Count -ge 9) 'Runtime inventory candidate does not declare the nine-file contract'
Assert-True ($runtimeInventoryCandidate -match 'FILTERED_BUILD_PLUGIN_COMPONENTS') 'Build-plugin metadata filtering is absent'
Assert-True ($runtimeInventoryCandidate -match 'FILTERED_METADATA_SUFFIXES\s*=\s*\("\.pom",\s*"\.module"\)') 'POM/module filtering is absent'
Assert-True ($runtimeInventoryCandidate -match 'ORDINARY_DEPENDENCY_LOCK_EVIDENCE_ONLY') 'Gradle lockfile role is not limited to ordinary dependency evidence'
Assert-True ($runtimeInventoryCandidate -match 'Plugin-managed Chaquopy runtime unexpectedly entered app/gradle\.lockfile') 'Plugin-managed runtime coordinates are not rejected from the ordinary Gradle lock'
Assert-True ($runtimeInventoryCandidate -match 'app"\s*/\s*"gradle\.lockfile') 'Runtime inventory candidate does not consume app/gradle.lockfile by default'
Assert-True ($runtimeInventoryCandidate -match 'gradle"\s*/\s*"verification-metadata\.xml') 'Runtime inventory candidate does not consume verification metadata by default'
Assert-True ($runtimeInventoryCandidate -match 'def verify_candidate\(') 'Runtime inventory candidate verification path is absent'
Assert-True ($runtimeInventoryCandidate -match 'REVIEW CANDIDATE ONLY - NOT A TRUST DECISION') 'Runtime inventory output is not marked as an untrusted review candidate'
Assert-True ($runtimeInventoryCandidate -notmatch '(?i)write_text\(|write_bytes\(|subprocess|os\.system|popen\(|\badb\b|gradlew') 'Runtime inventory candidate gained write or process capability'
Assert-True ($runtimeInventoryCandidateTest -match 'class RuntimeLockInventoryCandidateTest\(') 'Runtime inventory candidate tests are absent'
Assert-True ($runtimeInventoryCandidateTest -match 'test_rejects_missing_cache_artifact') 'Missing-artifact negative test is absent'
Assert-True ($runtimeInventoryCandidateTest -match 'test_rejects_explicit_artifact_with_wrong_bytes') 'Hash-mismatch negative test is absent'
Assert-True ($runtimeInventoryCandidateTest -match 'test_rejects_extra_runtime_binary_in_metadata') 'Extra-runtime-artifact negative test is absent'
Assert-True ($runtimeInventoryCandidateTest -match 'test_rejects_wrong_runtime_component_version') 'Wrong-runtime-version negative test is absent'
Assert-True ($runtimeInventoryCandidateTest -match 'test_rejects_wrong_abi_runtime_artifact') 'Wrong-runtime-ABI negative test is absent'
Assert-True (
    $readme -match '(?i)trusted-local,\s*non-sandbox|hostile-code sandbox' -or
    $readme -match '可信本地脚本.*(?:不是|不让).*沙箱'
) 'README trusted-local non-sandbox boundary is missing'
Assert-True ($runtimeAdr -match 'Chaquopy exposes a `?java`? module and `?jclass`?') 'Runtime-selection ADR does not record the Java bridge boundary'
Assert-True ($lockWorkflow -match '--write-locks --write-verification-metadata sha256') 'Supply-chain lock bootstrap workflow is absent'
Assert-True ($lockWorkflow -match '-Pautojs\.python\.runtime\.lock\.bootstrap=true') 'Bootstrap workflow does not require its explicit property'
Assert-True ($lockWorkflow -match 'canonical inventory digest') 'Per-artifact canonical inventory workflow is absent'
Assert-True ($lockWorkflow -match 'OFFICIAL_GRADLE_9_5_0_DISTRIBUTION_EMBEDDED_WRAPPER') 'Wrapper promotion provenance workflow is absent'

$expectedRuntimeLock = @{
    'format' = '2'
    'android.gradle.plugin.version' = '9.2.1'
    'chaquopy.plugin.version' = '17.0.0'
    'chaquopy.license' = 'MIT'
    'chaquopy.repository' = 'https://repo1.maven.org/maven2/com/chaquo/python/com.chaquo.python.gradle.plugin/17.0.0/'
    'python.version.requested' = '3.13'
    'python.version.expected' = '3.13.9'
    'python.license' = 'PSF-2.0'
    'python.implementation' = 'CPython'
    'android.minSdk' = '24'
    'android.targetSdk' = '36'
    'android.compileSdk' = '36'
    'android.abis' = 'arm64-v8a,x86_64'
    'python.packages.policy' = 'stdlib-only'
    'python.packages.count' = '0'
    'online.pip.allowed' = 'false'
}
foreach ($entry in $expectedRuntimeLock.GetEnumerator()) {
    Assert-True ($runtimeLock[$entry.Key] -eq $entry.Value) "Runtime lock mismatch: $($entry.Key)"
}
$runtimeArtifactState = Assert-RuntimeArtifactInventory $runtimeLock
$expectedRuntimeLockKeys = @($expectedRuntimeLock.Keys) + @(
    'runtime.artifacts.state',
    'runtime.artifacts.count',
    'runtime.artifacts.inventory.sha256'
) + @($runtimeLock.Keys | Where-Object { $_.StartsWith('runtime.artifact.') })
Assert-True ((($runtimeLock.Keys | Sort-Object) -join "`n") -ceq (($expectedRuntimeLockKeys | Sort-Object) -join "`n")) 'Runtime supply lock contains missing or unexpected keys'

$expectedWrapperLock = @{
    'format' = '1'
    'distribution.version' = '9.5.0'
    'distribution.url' = 'https://services.gradle.org/distributions/gradle-9.5.0-bin.zip'
    'distribution.sha256' = '553c78f50dafcd54d65b9a444649057857469edf836431389695608536d6b746'
    'wrapper.jar.expected.provenance' = 'OFFICIAL_GRADLE_9_5_0_DISTRIBUTION_EMBEDDED_WRAPPER'
    'wrapper.jar.source.entry' = 'gradle-9.5.0/lib/plugins/gradle-wrapper-main-9.5.0.jar!/gradle-wrapper.jar'
    'wrapper.jar.source.container.sha256' = '11954fe51c5f8d56321f694ebb2aec206c3871eab57e0bef4465b9c281003982'
}
foreach ($entry in $expectedWrapperLock.GetEnumerator()) {
    Assert-True ($wrapperLock[$entry.Key] -eq $entry.Value) "Gradle wrapper lock mismatch: $($entry.Key)"
}
$expectedWrapperLockKeys = @($expectedWrapperLock.Keys) + @(
    'wrapper.jar.state',
    'wrapper.jar.expected.sha256',
    'wrapper.jar.observed.sha256',
    'wrapper.jar.observed.provenance',
    'wrapper.jar.blocker'
)
Assert-True ((($wrapperLock.Keys | Sort-Object) -join "`n") -ceq (($expectedWrapperLockKeys | Sort-Object) -join "`n")) 'Gradle wrapper lock contains missing or unexpected keys'
$wrapperJar = Join-Path $repoRoot 'gradle/wrapper/gradle-wrapper.jar'
Assert-True (Test-Path -LiteralPath $wrapperJar -PathType Leaf) 'Gradle wrapper JAR is missing'
$actualWrapperSha256 = (Get-FileHash -LiteralPath $wrapperJar -Algorithm SHA256).Hash.ToLowerInvariant()
Assert-True ($wrapperLock['wrapper.jar.observed.sha256'] -ceq $actualWrapperSha256) 'Observed Gradle wrapper JAR SHA-256 does not match the checked-in JAR'
$wrapperProvenanceStatus = $null
if ($wrapperLock['wrapper.jar.state'] -eq 'BLOCKED') {
    Assert-True ($wrapperLock['wrapper.jar.expected.sha256'] -eq 'REQUIRED_OFFICIAL_GRADLE_9_5_0_WRAPPER_SHA256') 'Blocked wrapper must retain the target-version expected-hash marker'
    Assert-True ($actualWrapperSha256 -eq '7d3a4ac4de1c32b59bc6a4eb8ecb8e612ccd0cf1ae1e99f66902da64df296172') 'Unexpected blocked wrapper JAR hash'
    Assert-True ($wrapperLock['wrapper.jar.observed.provenance'] -eq 'OFFICIAL_GRADLE_8_14_EMBEDDED_WRAPPER') 'The blocked wrapper provenance must identify official Gradle 8.14'
    Assert-True ($wrapperLock['wrapper.jar.blocker'] -eq 'WRAPPER_JAR_VERSION_8_14_WITH_DISTRIBUTION_9_5_0') 'The wrapper version-mismatch blocker drifted'
    $wrapperProvenanceStatus = 'BLOCKED_VERSION_MISMATCH'
}
else {
    Assert-True ($wrapperLock['wrapper.jar.state'] -eq 'READY') 'Unsupported wrapper.jar.state'
    Assert-True ($wrapperLock['wrapper.jar.expected.sha256'] -match '^[0-9a-f]{64}$') 'READY wrapper requires a lowercase expected SHA-256'
    Assert-True ($wrapperLock['wrapper.jar.expected.sha256'] -ceq $actualWrapperSha256) 'READY wrapper expected SHA-256 does not match the checked-in JAR'
    Assert-True ($wrapperLock['wrapper.jar.observed.provenance'] -eq 'OFFICIAL_GRADLE_9_5_0_DISTRIBUTION_EMBEDDED_WRAPPER') 'READY wrapper observed provenance is not official Gradle 9.5.0'
    Assert-True ($wrapperLock['wrapper.jar.blocker'] -eq 'NONE') 'READY wrapper must not retain a blocker'
    $wrapperProvenanceStatus = 'READY'
}

$expectedAars = @('common-plugin-api', 'protocol-wire-api', 'python-runtime-api')
$expectedHostLockKeys = @('format') + @($expectedAars | ForEach-Object { @("$($_).file", "$($_).sha256") })
Assert-True ($hostLock['format'] -ceq '1') 'Unsupported host API AAR lock format'
Assert-True ((($hostLock.Keys | Sort-Object) -join "`n") -ceq (($expectedHostLockKeys | Sort-Object) -join "`n")) 'Host API AAR lock contains missing or unexpected keys'
$allHostAarsPresent = $true
foreach ($id in $expectedAars) {
    $fileName = $hostLock["$id.file"]
    $sha256 = $hostLock["$id.sha256"]
    Assert-True ($fileName -eq "$id.aar") "Unexpected AAR filename for $id"
    Assert-True (-not $fileName.EndsWith('-debug.aar')) "Debug AAR is forbidden: $fileName"
    $artifact = Join-Path $repoRoot "libs/$fileName"
    if (Test-Path -LiteralPath $artifact -PathType Leaf) {
        Assert-True ($sha256 -match '^[0-9a-f]{64}$') "A real SHA-256 is required for staged $fileName"
        $actual = (Get-FileHash -LiteralPath $artifact -Algorithm SHA256).Hash.ToLowerInvariant()
        Assert-True ($actual -eq $sha256) "SHA-256 mismatch for staged $fileName"
    }
    else {
        $allHostAarsPresent = $false
        Assert-True ($sha256 -eq 'REQUIRED_SHA256') "Missing $fileName must retain the fail-closed placeholder"
    }
}

$unexpectedAars = @(Get-ChildItem -LiteralPath (Join-Path $repoRoot 'libs') -Filter '*.aar' -File | Where-Object {
    $_.Name -notin @('common-plugin-api.aar', 'protocol-wire-api.aar', 'python-runtime-api.aar')
})
Assert-True ($unexpectedAars.Count -eq 0) 'Unexpected AAR exists under libs'

$localeDirectories = @(
    'values', 'values-ar', 'values-es', 'values-fr', 'values-ja',
    'values-ko', 'values-ru', 'values-zh', 'values-zh-rHK', 'values-zh-rTW'
)
foreach ($directory in $localeDirectories) {
    $relativePath = "app/src/main/res/$directory/strings.xml"
    $strings = Read-RequiredText $relativePath
    Assert-True ($strings -match 'name="plugin_description"') "Missing plugin_description in $relativePath"
}

Assert-True ($roadmap -match 'R6-P2: final source and Host-pair freeze') 'Stable source and Host-pair freeze stage is missing from the roadmap'
Assert-True ($roadmap -match 'Existing\s+RC receipts are historical') 'Historical RC evidence boundary is missing from the roadmap'
Assert-True ($roadmap -match 'complete API 24-36 by ABI matrix.*not automatic' -or $roadmap -match '(?s)complete API 24-36 by ABI matrix.*not automatic') 'Risk-proportional device evidence policy is missing from the roadmap'
Assert-True ($roadmap -match 'production receipt') 'Independent production receipt boundary is missing from the roadmap'

$validBootstrap = @{
    PropertyValue = 'true'
    Tasks = @(':app:testDebugUnitTest', ':app:lintDebug', ':app:assembleDebug')
    WriteLocks = $true
    HasUpdatedLocks = $false
    VerificationAlgorithms = @('sha256')
    ExcludedTasks = @()
    DryRun = $false
}
Assert-True (Test-RuntimeLockBootstrapAdmission @validBootstrap) 'Bootstrap admission model rejects its sole valid input'
$bootstrapNegativeCases = @(
    @{ Name = 'missing-property'; Changes = @{ PropertyValue = $null } },
    @{ Name = 'false-property'; Changes = @{ PropertyValue = 'false' } },
    @{ Name = 'malformed-property'; Changes = @{ PropertyValue = 'TRUE' } },
    @{ Name = 'arbitrary-task'; Changes = @{ Tasks = @(':help') } },
    @{ Name = 'task-subset'; Changes = @{ Tasks = @(':app:assembleDebug', ':app:lintDebug') } },
    @{ Name = 'duplicate-task'; Changes = @{ Tasks = @(':app:assembleDebug', ':app:lintDebug', ':app:lintDebug') } },
    @{ Name = 'extra-device-task'; Changes = @{ Tasks = @(':app:assembleDebug', ':app:lintDebug', ':app:testDebugUnitTest', ':app:connectedDebugAndroidTest') } },
    @{ Name = 'release-task'; Changes = @{ Tasks = @(':app:assembleRelease', ':app:lintDebug', ':app:testDebugUnitTest') } },
    @{ Name = 'missing-write-locks'; Changes = @{ WriteLocks = $false } },
    @{ Name = 'update-locks'; Changes = @{ HasUpdatedLocks = $true } },
    @{ Name = 'missing-verification-write'; Changes = @{ VerificationAlgorithms = @() } },
    @{ Name = 'extra-verification-algorithm'; Changes = @{ VerificationAlgorithms = @('sha256', 'sha512') } },
    @{ Name = 'excluded-task'; Changes = @{ ExcludedTasks = @(':app:lintDebug') } },
    @{ Name = 'dry-run'; Changes = @{ DryRun = $true } }
)
foreach ($case in $bootstrapNegativeCases) {
    $arguments = @{}
    foreach ($key in $validBootstrap.Keys) { $arguments[$key] = $validBootstrap[$key] }
    foreach ($key in $case.Changes.Keys) { $arguments[$key] = $case.Changes[$key] }
    Assert-True (-not (Test-RuntimeLockBootstrapAdmission @arguments)) "Bootstrap negative case was admitted: $($case.Name)"
}

Write-Output 'R2_STATIC_GATE=PASS'
Write-Output 'EVIDENCE_SCOPE=FILESYSTEM_STATIC_SCAFFOLD_ONLY'
Write-Output 'RUNTIME_SOURCE=PRESENT_STATIC_GATE_DOES_NOT_PROVE_COMPILE'
Write-Output 'LOCAL_BOOTSTRAP_TEST=SEPARATE_NON_ANDROID_EVIDENCE'
Write-Output 'STATIC_GATE_GRADLE_EXECUTED=NO'
Write-Output 'STATIC_GATE_ADB_EXECUTED=NO'
Write-Output "HOST_AARS=$(if ($allHostAarsPresent) { 'HASH_PINNED_RELEASE_TRIPLET' } else { 'DEFERRED_FAIL_CLOSED' })"
Write-Output "RUNTIME_ARTIFACT_HASHES=$($runtimeArtifactState)_FAIL_CLOSED"
Write-Output "GRADLE_WRAPPER_PROVENANCE=$wrapperProvenanceStatus"
Write-Output "GRADLE_BUILD_ADMISSION=$(if (-not $allHostAarsPresent) { 'BLOCKED_RUNTIME_AND_HOST_LOCKS' } elseif ($runtimeArtifactState -eq 'RESOLVED') { 'ORDINARY_CONFIGURATION_READY' } else { 'BOOTSTRAP_ONLY_RUNTIME_LOCK' })"
Write-Output "RUNTIME_LOCK_BOOTSTRAP_NEGATIVE_CASES=$($bootstrapNegativeCases.Count)_PASS"
Write-Output 'RUNTIME_INVENTORY_CANDIDATE=READ_ONLY_REVIEW_ONLY'
Write-Output 'DEFERRED_DEVICE_PLAN=PRESENT_NOT_EXECUTABLE'
Write-Output 'DEVICE_RUNNER=NOT_INSPECTED_BY_THIS_STATIC_GATE'
Write-Output 'DEVICE_RECEIPT=NOT_CREATED'
Write-Output 'DEVICE_ACCEPTANCE=NOT_CLAIMED'
