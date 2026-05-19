@echo off
setlocal
py -3 "%~dp0tool_semantic_impact.py" %*
exit /b %errorlevel%
