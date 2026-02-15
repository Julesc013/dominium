@echo off
setlocal EnableExtensions

if "%~1"=="" goto usage

python tools\xstack\srz_status.py --repo-root . %*
set "rc=%ERRORLEVEL%"
endlocal & exit /b %rc%

:usage
echo Usage: tools\xstack\srz_status ^<session_spec_path^>
echo Example: tools\xstack\srz_status saves\save.lab.bootstrap\session_spec.json
endlocal & exit /b 2
