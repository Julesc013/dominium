@echo off
setlocal EnableExtensions

if "%~1"=="" goto usage

python tools\xstack\run.py %*
set "rc=%ERRORLEVEL%"
endlocal & exit /b %rc%

:usage
echo Usage:
echo   tools\xstack\run fast [--cache on^|off]
echo   tools\xstack\run strict [--cache on^|off]
echo   tools\xstack\run full [--shards N] [--shard-index I] [--cache on^|off]
endlocal & exit /b 2
