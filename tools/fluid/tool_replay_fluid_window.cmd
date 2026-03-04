@echo off
setlocal
py -3 "%~dp0tool_replay_fluid_window.py" %*
exit /b %errorlevel%
