@echo off
setlocal EnableExtensions

python tools\xstack\pack_loader\pack_list.py --repo-root .
set "rc=%ERRORLEVEL%"
endlocal & exit /b %rc%

