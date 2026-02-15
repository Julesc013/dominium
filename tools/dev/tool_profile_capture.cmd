@echo off
setlocal
python "%~dp0tool_profile_capture.py" %*
exit /b %errorlevel%
