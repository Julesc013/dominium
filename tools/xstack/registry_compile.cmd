@echo off
setlocal EnableExtensions

python tools\xstack\registry_compile\registry_compile.py --repo-root . %*
set "rc=%ERRORLEVEL%"
endlocal & exit /b %rc%

