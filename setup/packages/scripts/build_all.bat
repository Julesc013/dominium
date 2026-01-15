@echo off
setlocal EnableExtensions

set "ROOT=%~dp0.."
pushd "%ROOT%" >nul

set "BUILD_DIR=%~1"
if "%BUILD_DIR%"=="" set "BUILD_DIR=build\\release_ready"
set "CONFIG=%~2"
if "%CONFIG%"=="" set "CONFIG=Debug"

if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%"

echo Configuring build in %BUILD_DIR%...
cmake -S . -B "%BUILD_DIR%" -DCMAKE_BUILD_TYPE=%CONFIG% ^
  -DDOM_DISALLOW_DOWNLOADS=ON ^
  -DFETCHCONTENT_FULLY_DISCONNECTED=ON ^
  -DFETCHCONTENT_UPDATES_DISCONNECTED=ON
if errorlevel 1 goto :fail

echo Building...
cmake --build "%BUILD_DIR%" --config %CONFIG%
if errorlevel 1 goto :fail

echo Build all: PASS
popd >nul
exit /b 0

:fail
echo Build all: FAIL
popd >nul
exit /b 1
