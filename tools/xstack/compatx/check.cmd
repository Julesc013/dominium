@echo off
setlocal EnableExtensions

python tools\xstack\compatx\check.py --repo-root . %*
set "rc=%ERRORLEVEL%"
endlocal & exit /b %rc%

