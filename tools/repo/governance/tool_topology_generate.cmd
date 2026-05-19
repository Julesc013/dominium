@echo off
setlocal
py -3 "%~dp0tool_topology_generate.py" %*
exit /b %errorlevel%
