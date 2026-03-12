@echo off
setlocal
py -3 "%~dp0tool_run_cross_platform_matrix.py" %*
exit /b %errorlevel%
