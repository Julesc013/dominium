@echo off
setlocal EnableExtensions

python tools\xstack\registry_compile\lockfile_build.py --repo-root . %*
set "rc=%ERRORLEVEL%"
endlocal & exit /b %rc%

