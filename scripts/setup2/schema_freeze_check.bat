@echo off
setlocal enabledelayedexpansion

set ROOT=%~dp0\..\..
for %%I in ("%ROOT%") do set ROOT=%%~fI

cmake -P "%ROOT%\scripts\setup2\schema_freeze_check.cmake"
exit /b %ERRORLEVEL%

