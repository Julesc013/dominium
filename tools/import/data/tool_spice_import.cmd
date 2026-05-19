@echo off
setlocal EnableExtensions

python tools\data\tool_spice_import.py --repo-root . %*
set "rc=%ERRORLEVEL%"
endlocal & exit /b %rc%

