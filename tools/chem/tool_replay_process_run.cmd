@echo off
setlocal
py -3 "%~dp0tool_replay_process_run.py" %*
exit /b %errorlevel%
