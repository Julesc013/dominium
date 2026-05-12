@echo off
setlocal EnableExtensions

set "ROOT=%~dp0.."
pushd "%ROOT%" >nul

set "LOG_DIR=build\\verify_release_logs"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

set "CONFIG=%~1"
if "%CONFIG%"=="" set "CONFIG=Debug"

echo Running build_all...
call scripts\\build_all.bat "build\\release_ready" "%CONFIG%" > "%LOG_DIR%\\build_all.log" 2>&1
if errorlevel 1 goto :fail

echo Running test_all...
call scripts\\test_all.bat > "%LOG_DIR%\\test_all.log" 2>&1
if errorlevel 1 goto :fail

echo verify_release: PASS
echo Logs: %LOG_DIR%
popd >nul
exit /b 0

:fail
echo verify_release: FAIL
echo Logs: %LOG_DIR%
popd >nul
exit /b 1
