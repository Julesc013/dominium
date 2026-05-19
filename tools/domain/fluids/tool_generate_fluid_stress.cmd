@echo off
setlocal
py -3 "%~dp0tool_generate_fluid_stress.py" %*
exit /b %errorlevel%
