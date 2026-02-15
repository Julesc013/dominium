@echo off
setlocal EnableExtensions

if "%~1"=="" goto usage

python tools\xstack\registry_compile\lockfile_validate.py --repo-root . "%~1"
set "rc=%ERRORLEVEL%"
endlocal & exit /b %rc%

:usage
echo Usage: tools\xstack\lockfile_validate ^<lockfile_path^>
echo Example: tools\xstack\lockfile_validate build\lockfile.json
endlocal & exit /b 2

