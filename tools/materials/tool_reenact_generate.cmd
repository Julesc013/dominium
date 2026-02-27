@echo off
setlocal
py -3 "%~dp0tool_reenact_generate.py" %*
exit /b %errorlevel%
