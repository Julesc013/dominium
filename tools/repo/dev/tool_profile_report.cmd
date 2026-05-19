@echo off
setlocal
python "%~dp0tool_profile_report.py" %*
exit /b %errorlevel%
