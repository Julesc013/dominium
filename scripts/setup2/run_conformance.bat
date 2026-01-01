@echo off
setlocal

set ROOT=%~dp0\..\..
for %%I in ("%ROOT%") do set ROOT=%%~fI
set PRESET=%1
if "%PRESET%"=="" set PRESET=msvc-debug

set LOG_DIR=%ROOT%\dist\setup2\conformance
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
set LOG=%LOG_DIR%\conformance.log
set BUILD_DIR=%ROOT%\build\%PRESET%
set SUMMARY_SRC=%BUILD_DIR%\source\tests\setup2_conformance\conformance_summary.json
set SUMMARY_DST=%LOG_DIR%\conformance_summary.json

> "%LOG%" echo ^>^> ctest --preset %PRESET% -R setup2_conformance --output-on-failure
ctest --preset %PRESET% -R setup2_conformance --output-on-failure >> "%LOG%" 2>&1
if exist "%SUMMARY_SRC%" copy /Y "%SUMMARY_SRC%" "%SUMMARY_DST%" >nul
exit /b %errorlevel%
