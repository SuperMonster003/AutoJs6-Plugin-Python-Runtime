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
    [switch] $ConfirmDeviceMutation
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$core = Join-Path $PSScriptRoot 'run-u1-r1-binder-cpython-device.ps1'
if (-not (Test-Path -LiteralPath $core -PathType Leaf)) {
    throw "Shared exact-device runner is missing: $core"
}

$forward = @{
    Serial = $Serial
    ExpectedApi = $ExpectedApi
    ExpectedAbi = $ExpectedAbi
    ExpectedUserIds = $ExpectedUserIds
    HostRepository = $HostRepository
    PluginRepository = $PluginRepository
    ExpectedHostCommit = $ExpectedHostCommit
    ExpectedPluginCommit = $ExpectedPluginCommit
    FunctionalGate = $FunctionalGate
    FunctionalGateSha256 = $FunctionalGateSha256
    ObservationFixture = $ObservationFixture
    ObservationFixtureSha256 = $ObservationFixtureSha256
    HostApk = $HostApk
    HostSha256 = $HostSha256
    HostTestApk = $HostTestApk
    HostTestSha256 = $HostTestSha256
    PluginApk = $PluginApk
    PluginSha256 = $PluginSha256
    ExpectedSignerSha256 = $ExpectedSignerSha256
    AdbPath = $AdbPath
    Aapt2Path = $Aapt2Path
    ApkSignerPath = $ApkSignerPath
    Output = $Output
    ConfirmNoActiveSoak = $ConfirmNoActiveSoak
    ConfirmDeviceMutation = $ConfirmDeviceMutation
    EvidenceProfile = 'U1-R2'
}

& $core @forward
