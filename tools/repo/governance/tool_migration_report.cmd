@echo off
setlocal
py -3 "%~dp0tool_migration_report.py" %*
exit /b %errorlevel%
