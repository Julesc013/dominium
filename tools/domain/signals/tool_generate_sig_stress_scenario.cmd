@echo off
setlocal
py -3 "%~dp0tool_generate_sig_stress_scenario.py" %*
exit /b %errorlevel%

