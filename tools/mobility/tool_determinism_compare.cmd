@echo off
setlocal
py -3 "%~dp0tool_determinism_compare.py" %*
exit /b %errorlevel%
