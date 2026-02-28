@echo off
setlocal
py -3 "%~dp0tool_deprecation_check.py" %*
exit /b %errorlevel%
