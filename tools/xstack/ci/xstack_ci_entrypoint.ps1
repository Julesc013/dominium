$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
& python "$ScriptDir/xstack_ci_entrypoint.py" @args
exit $LASTEXITCODE
