@echo off
setlocal EnableExtensions

python tools\xstack\bundle_list.py --repo-root . %*
set "rc=%ERRORLEVEL%"
endlocal & exit /b %rc%
