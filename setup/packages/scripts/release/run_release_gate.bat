@echo off
setlocal enabledelayedexpansion

set ROOT=%~dp0\..\..
for %%I in ("%ROOT%") do set ROOT=%%~fI
set LOG_DIR=%ROOT%\dist\release_gate
set LOG_DIR_REL=dist/release_gate

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

set BUILD_LOG=%LOG_DIR%\build.log
set SETUP_LOG=%LOG_DIR%\setup_tests.log
set LAUNCHER_LOG=%LOG_DIR%\launcher_smoke.log
set PACKAGING_LOG=%LOG_DIR%\packaging_validation.log

set BUILD_STATUS=pass
set SETUP_STATUS=pass
set LAUNCHER_STATUS=pass
set PACKAGING_STATUS=pass

> "%BUILD_LOG%" echo ^>^> cmake --build --preset debug
cmake --build --preset debug >> "%BUILD_LOG%" 2>&1
if errorlevel 1 set BUILD_STATUS=fail

> "%SETUP_LOG%" echo ^>^> ctest --preset debug -R dsu_ -E dsu_packaging_validation_test --output-on-failure
ctest --preset debug -R dsu_ -E dsu_packaging_validation_test --output-on-failure >> "%SETUP_LOG%" 2>&1
if errorlevel 1 set SETUP_STATUS=fail

>> "%SETUP_LOG%" echo ^>^> ctest --preset debug -R test_ --output-on-failure
ctest --preset debug -R test_ --output-on-failure >> "%SETUP_LOG%" 2>&1
if errorlevel 1 set SETUP_STATUS=fail

> "%LAUNCHER_LOG%" echo ^>^> ctest --preset debug -R dominium_launcher_state_smoke_tests --output-on-failure
ctest --preset debug -R dominium_launcher_state_smoke_tests --output-on-failure >> "%LAUNCHER_LOG%" 2>&1
if errorlevel 1 set LAUNCHER_STATUS=fail

>> "%LAUNCHER_LOG%" echo ^>^> ctest --preset debug -R dominium_launcher_ui_smoke_tests --output-on-failure
ctest --preset debug -R dominium_launcher_ui_smoke_tests --output-on-failure >> "%LAUNCHER_LOG%" 2>&1
if errorlevel 1 set LAUNCHER_STATUS=fail

>> "%LAUNCHER_LOG%" echo ^>^> ctest --preset debug -R dominium_launcher_tui_smoke_tests --output-on-failure
ctest --preset debug -R dominium_launcher_tui_smoke_tests --output-on-failure >> "%LAUNCHER_LOG%" 2>&1
if errorlevel 1 set LAUNCHER_STATUS=fail

> "%PACKAGING_LOG%" echo ^>^> ctest --preset debug -R dsu_packaging_validation_test --output-on-failure
ctest --preset debug -R dsu_packaging_validation_test --output-on-failure >> "%PACKAGING_LOG%" 2>&1
if errorlevel 1 set PACKAGING_STATUS=fail

set OVERALL=pass
if not "%BUILD_STATUS%"=="pass" set OVERALL=fail
if not "%SETUP_STATUS%"=="pass" set OVERALL=fail
if not "%LAUNCHER_STATUS%"=="pass" set OVERALL=fail
if not "%PACKAGING_STATUS%"=="pass" set OVERALL=fail

set SUMMARY=%LOG_DIR%\release_gate_summary.json
(
echo {
echo   "schema_version": 1,
echo   "log_dir": "%LOG_DIR_REL%",
echo   "stages": [
echo     {"name":"build","status":"%BUILD_STATUS%","log":"%LOG_DIR_REL%/build.log"},
echo     {"name":"setup_tests","status":"%SETUP_STATUS%","log":"%LOG_DIR_REL%/setup_tests.log"},
echo     {"name":"launcher_smoke","status":"%LAUNCHER_STATUS%","log":"%LOG_DIR_REL%/launcher_smoke.log"},
echo     {"name":"packaging_validation","status":"%PACKAGING_STATUS%","log":"%LOG_DIR_REL%/packaging_validation.log"}
echo   ],
echo   "overall":"%OVERALL%"
echo }
) > "%SUMMARY%"

if not "%OVERALL%"=="pass" exit /b 1
exit /b 0
