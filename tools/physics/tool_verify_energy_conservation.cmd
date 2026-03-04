@echo off
setlocal
py -3 "%~dp0tool_verify_energy_conservation.py" %*
exit /b %errorlevel%
