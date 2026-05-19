@echo off
setlocal
py -3 "%~dp0tool_replay_elec_window.py" %*
exit /b %errorlevel%
