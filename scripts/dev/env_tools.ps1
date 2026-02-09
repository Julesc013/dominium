$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $scriptDir "..\..")).Path

$exportLines = & python "$scriptDir\env_tools.py" --repo-root $repoRoot export --shell powershell
if ($LASTEXITCODE -ne 0) {
    $exportLines | ForEach-Object { Write-Host $_ }
    exit $LASTEXITCODE
}

$exportScript = ($exportLines -join [Environment]::NewLine)
Invoke-Expression $exportScript

& python "$scriptDir\env_tools.py" --repo-root $repoRoot doctor --require-path
exit $LASTEXITCODE
