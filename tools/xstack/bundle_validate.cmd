@echo off
setlocal EnableExtensions

if "%~1"=="" goto usage

python tools\xstack\bundle_validate.py --repo-root . %*
set "rc=%ERRORLEVEL%"
endlocal & exit /b %rc%

:usage
echo Usage: tools\xstack\bundle_validate ^<bundle_json_path^>
echo Example: tools\xstack\bundle_validate bundles\bundle.base.lab\bundle.json
endlocal & exit /b 2
