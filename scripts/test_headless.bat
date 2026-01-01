@echo off
setlocal EnableExtensions

set "ROOT=%~dp0.."
pushd "%ROOT%" >nul

set "BUILD_DIR=%~1"
if "%BUILD_DIR%"=="" set "BUILD_DIR=build\\headless_checks"
set "CONFIG=%~2"
if "%CONFIG%"=="" set "CONFIG=Debug"

if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%"

echo Configuring headless build in %BUILD_DIR%...
cmake -S . -B "%BUILD_DIR%" -DCMAKE_BUILD_TYPE=%CONFIG% ^
  -DDOM_DISALLOW_DOWNLOADS=ON ^
  -DFETCHCONTENT_FULLY_DISCONNECTED=ON ^
  -DFETCHCONTENT_UPDATES_DISCONNECTED=ON ^
  -DDOM_PLATFORM=null ^
  -DDOM_BACKEND_NULL=ON ^
  -DDOM_BACKEND_SOFT=OFF ^
  -DDOM_BACKEND_DX9=OFF
if errorlevel 1 goto :fail

echo Building headless targets...
cmake --build "%BUILD_DIR%" --config %CONFIG%
if errorlevel 1 goto :fail

echo Running layer checks...
python scripts\check_layers.py
if errorlevel 1 goto :fail

echo Running headless tests...
set "TEST_REGEX=dominium_launcher_control_plane_tests|dominium_launcher_artifact_store_tx_tests|dominium_launcher_prelaunch_recovery_tests|dominium_contract_|dominium_tlv_fuzz|launcher_kernel_smoke|setup_kernel_smoke|setup2_"
ctest --test-dir "%BUILD_DIR%" --output-on-failure -C %CONFIG% -R "%TEST_REGEX%"
if errorlevel 1 goto :fail

echo Headless tests: PASS
popd >nul
exit /b 0

:fail
echo Headless tests: FAIL
popd >nul
exit /b 1
