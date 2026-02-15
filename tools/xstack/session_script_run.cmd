@echo off
setlocal EnableExtensions

if "%~1"=="" goto usage
if "%~2"=="" goto usage

python tools\xstack\session_script_run.py --repo-root . %*
set "rc=%ERRORLEVEL%"
endlocal & exit /b %rc%

:usage
echo Usage: tools\xstack\session_script_run ^<session_spec_path^> ^<script_path^> [--bundle bundle.base.lab] [--workers N] [--logical-shards N]
echo Example: tools\xstack\session_script_run saves\save.lab.bootstrap\session_spec.json tools\xstack\testdata\session\script.camera_nav.fixture.json --workers 1 --logical-shards 1
endlocal & exit /b 2
