@echo off
setlocal EnableExtensions

set "ROOT=%~dp0.."
pushd "%ROOT%" >nul

set "BUILD_DIR=build\\all_checks"
set "CONFIG=Debug"

echo Running launcher core invariants...
python scripts\ci\check_launcher_core_invariants.py
if errorlevel 1 goto :fail

if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%"

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
ctest --test-dir "%BUILD_DIR%" --output-on-failure -C %CONFIG%
if errorlevel 1 goto :fail

echo Launcher CLI smoke matrix...
python scripts\ci\launcher_cli_smoke_matrix.py --build-dir "%BUILD_DIR%"
if errorlevel 1 goto :fail

echo Support bundle determinism...
python scripts\ci\test_support_bundle_determinism.py --out-dir "%BUILD_DIR%\\ci_artifacts\\support_bundle"
if errorlevel 1 goto :fail

echo Headless acceptance flows...
call scripts\test_headless.bat
if errorlevel 1 goto :fail

echo Full tests: PASS
popd >nul
exit /b 0

:fail
echo Full tests: FAIL
popd >nul
exit /b 1
