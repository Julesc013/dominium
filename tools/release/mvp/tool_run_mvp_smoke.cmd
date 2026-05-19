@echo off
setlocal
py -3 "%~dp0tool_run_mvp_smoke.py" %*
exit /b %errorlevel%
