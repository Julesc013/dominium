@echo off
setlocal EnableExtensions

python tools\setup\build.py --repo-root . %*
set "rc=%ERRORLEVEL%"
endlocal & exit /b %rc%

