@echo off
setlocal
py -3 "%~dp0tool_run_fluid_stress.py" %*
exit /b %errorlevel%
