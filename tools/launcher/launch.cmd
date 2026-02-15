@echo off
setlocal EnableExtensions

python tools\launcher\launch.py --repo-root . %*
set "rc=%ERRORLEVEL%"
endlocal & exit /b %rc%

