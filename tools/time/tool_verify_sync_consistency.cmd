@echo off
setlocal
py -3 "%~dp0tool_verify_sync_consistency.py" %*
exit /b %errorlevel%
