@echo off
setlocal EnableExtensions

set "ROOT=%~dp0.."
pushd "%ROOT%" >nul

set "BUILD_DIR=build\\all_checks"
set "CONFIG=Debug"

echo Configuring full test build in %BUILD_DIR%...
cmake -S . -B "%BUILD_DIR%" -DCMAKE_BUILD_TYPE=%CONFIG% ^
  -DDOM_DISALLOW_DOWNLOADS=ON ^
  -DFETCHCONTENT_FULLY_DISCONNECTED=ON ^
  -DFETCHCONTENT_UPDATES_DISCONNECTED=ON
if errorlevel 1 goto :fail

echo Building...
cmake --build "%BUILD_DIR%" --config %CONFIG%
if errorlevel 1 goto :fail

echo Running layer checks...
python scripts\check_layers.py
if errorlevel 1 goto :fail

echo Running tests...
ctest --test-dir "%BUILD_DIR%" --output-on-failure
if errorlevel 1 goto :fail

echo Full tests: PASS
popd >nul
exit /b 0

:fail
echo Full tests: FAIL
popd >nul
exit /b 1
