@echo off
setlocal EnableExtensions

set "ROOT=%~dp0.."
pushd "%ROOT%" >nul

set "BUILD_DIR=build\\kernel_checks"
set "CONFIG=Debug"

echo Configuring kernel checks in %BUILD_DIR%...
cmake -S . -B "%BUILD_DIR%" -DCMAKE_BUILD_TYPE=%CONFIG% ^
  -DDOM_DISALLOW_DOWNLOADS=ON ^
  -DFETCHCONTENT_FULLY_DISCONNECTED=ON ^
  -DFETCHCONTENT_UPDATES_DISCONNECTED=ON ^
  -DDOM_PLATFORM=null ^
  -DDOM_BACKEND_NULL=ON ^
  -DDOM_BACKEND_SOFT=OFF
if errorlevel 1 goto :fail

echo Building kernel smoke targets...
cmake --build "%BUILD_DIR%" --config %CONFIG% --target launcher_kernel_smoke setup_kernel_smoke
if errorlevel 1 goto :fail

echo Running kernel layer checks and smoke tests...
ctest --test-dir "%BUILD_DIR%" --output-on-failure -R "dominium_layer_checks|launcher_kernel_smoke|setup_kernel_smoke"
if errorlevel 1 goto :fail

echo Kernel checks: PASS
popd >nul
exit /b 0

:fail
echo Kernel checks: FAIL
popd >nul
exit /b 1
