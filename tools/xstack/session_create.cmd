@echo off
setlocal EnableExtensions

python tools\xstack\session_create.py --repo-root . %*
set "rc=%ERRORLEVEL%"
endlocal & exit /b %rc%
