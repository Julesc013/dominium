@echo off
setlocal
py -3 "%~dp0tool_blueprint_compile.py" %*
exit /b %errorlevel%
