@echo off
setlocal
py -3 "%~dp0tool_verify_mass_conservation.py" %*
exit /b %errorlevel%
