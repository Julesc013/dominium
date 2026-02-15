@echo off
setlocal EnableExtensions

if "%~1"=="" goto usage

python tools\xstack\session_boot.py --repo-root . %*
set "rc=%ERRORLEVEL%"
endlocal & exit /b %rc%

:usage
echo Usage: tools\xstack\session_boot ^<session_spec_path^> [--bundle bundle.base.lab] [--compile-if-missing on^|off]
echo Example: tools\xstack\session_boot saves\save.lab\session_spec.json --compile-if-missing on
endlocal & exit /b 2
