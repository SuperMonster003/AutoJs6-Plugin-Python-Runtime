[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[A-Za-z0-9._:-]+$')]
    [string] $Serial,

    [Parameter(Mandatory = $true)]
    [string] $DevicePath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$expectedBytes = 34L
$expectedHash = '2B4A5E4BB7EB7C83D6241C5176D01EEDD31873FA63B28DE10F5553D8FBD25BD4'
if (
    ($DevicePath -notlike '/storage/emulated/0/*' -and $DevicePath -notlike '/sdcard/*') -or
    $DevicePath -notlike '*/m6/expected.bin' -or
    $DevicePath.IndexOf([char]0) -ge 0
) {
    throw "Unexpected device artifact path: $DevicePath"
}

$temporaryFile = Join-Path `
    ([System.IO.Path]::GetTempPath()) `
    ("autojs6-m6-04-{0}.bin" -f [Guid]::NewGuid().ToString('N'))
try {
    & adb -s $Serial pull $DevicePath $temporaryFile
    if ($LASTEXITCODE -ne 0) {
        throw "adb pull failed with exit code $LASTEXITCODE"
    }
    $item = Get-Item -LiteralPath $temporaryFile
    $actualHash = (Get-FileHash -LiteralPath $temporaryFile -Algorithm SHA256).Hash
    if ($item.Length -ne $expectedBytes) {
        throw "Artifact length mismatch: expected=$expectedBytes actual=$($item.Length)"
    }
    if ($actualHash -ne $expectedHash) {
        throw "Artifact SHA-256 mismatch: expected=$expectedHash actual=$actualHash"
    }
    Write-Output "M6-04-ARTIFACT-PASS bytes=$($item.Length) sha256=$actualHash"
}
finally {
    if (Test-Path -LiteralPath $temporaryFile) {
        Remove-Item -LiteralPath $temporaryFile -Force
    }
}
