@echo off
setlocal
py -3 "%~dp0tool_verify_entropy_monotonicity.py" %*
exit /b %errorlevel%
