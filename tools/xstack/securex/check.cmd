@echo off
setlocal EnableExtensions

python tools\xstack\securex\check.py --repo-root . %*
set "rc=%ERRORLEVEL%"
endlocal & exit /b %rc%

