@echo off
setlocal
py -3 "%~dp0tool_generate_chem_stress.py" %*
exit /b %errorlevel%
