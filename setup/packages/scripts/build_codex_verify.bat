@echo off
setlocal EnableExtensions EnableDelayedExpansion

rem Codex verification (Prompt 8).
rem - Builds a small canonical matrix in isolated build dirs.
rem - Runs system smoke, gfx demo, launcher smoke GUI, and game smoke GUI.
rem - No downloads (DOM_DISALLOW_DOWNLOADS=ON).

set "ROOT=%~dp0.."
pushd "%ROOT%" >nul

rem Prefer the repo's canonical MSYS2 UCRT64 toolchain for Ninja builds.
set "PATH=C:\msys64\ucrt64\bin;C:\msys64\usr\bin;%PATH%"
set "CC=C:/msys64/ucrt64/bin/cc.exe"
set "CXX=C:/msys64/ucrt64/bin/c++.exe"

set "FAIL_NAME="
set "FAIL_STAGE="
set "FAIL_DIR="
set "FAIL_CMD="

echo Codex verify gate: scripts\build_codex_verify.bat
echo Root: %CD%

call :run_entry "baseline win32 + soft" "build\\baseline-debug" ^
  "cmake --preset baseline-debug -DDOM_DISALLOW_DOWNLOADS=ON" ^
  "cmake --build --preset baseline-debug" ^
  "build\\baseline-debug\\domino_sys_smoke.exe --smoke" ^
  "build\\baseline-debug\\dgfx_demo.exe --gfx=soft --frames=120" ^
  "build\\baseline-debug\\source\\dominium\\launcher\\dominium-launcher.exe --smoke-gui --gfx=soft --profile=baseline" ^
  "build\\baseline-debug\\source\\dominium\\game\\dominium_game.exe --smoke-gui --gfx=soft --profile=baseline"
if errorlevel 1 goto :summary_fail

call :run_entry_optional "baseline win32 + dx9 (optional)" "build\\codex_verify\\baseline_win32_dx9" ^
  "cmake -S . -B build/codex_verify/baseline_win32_dx9 -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_C_COMPILER=%CC% -DCMAKE_CXX_COMPILER=%CXX% -DDOM_DISALLOW_DOWNLOADS=ON -DFETCHCONTENT_FULLY_DISCONNECTED=ON -DFETCHCONTENT_UPDATES_DISCONNECTED=ON -DDOM_PLATFORM=win32 -DDOM_BACKEND_SOFT=OFF -DDOM_BACKEND_DX9=ON -DDOM_BACKEND_NULL=OFF" ^
  "cmake --build build/codex_verify/baseline_win32_dx9 --target dgfx_demo dominium-launcher dominium_game" ^
  "build\\codex_verify\\baseline_win32_dx9\\dgfx_demo.exe --gfx=dx9 --frames=120" ^
  "build\\codex_verify\\baseline_win32_dx9\\source\\dominium\\launcher\\dominium-launcher.exe --smoke-gui --gfx=dx9 --profile=baseline" ^
  "build\\codex_verify\\baseline_win32_dx9\\source\\dominium\\game\\dominium_game.exe --smoke-gui --gfx=dx9 --profile=baseline"
if errorlevel 1 goto :summary_fail

call :run_entry "baseline win32_headless + soft" "build\\codex_verify\\baseline_win32_headless_soft" ^
  "cmake -S . -B build/codex_verify/baseline_win32_headless_soft -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_C_COMPILER=%CC% -DCMAKE_CXX_COMPILER=%CXX% -DDOM_DISALLOW_DOWNLOADS=ON -DFETCHCONTENT_FULLY_DISCONNECTED=ON -DFETCHCONTENT_UPDATES_DISCONNECTED=ON -DDOM_PLATFORM=win32_headless -DDOM_BACKEND_SOFT=ON -DDOM_BACKEND_NULL=OFF" ^
  "cmake --build build/codex_verify/baseline_win32_headless_soft --target domino_sys_smoke" ^
  "build\\codex_verify\\baseline_win32_headless_soft\\domino_sys_smoke.exe --smoke"
if errorlevel 1 goto :summary_fail

call :run_entry "baseline null + null" "build\\codex_verify\\baseline_null_null" ^
  "cmake -S . -B build/codex_verify/baseline_null_null -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_C_COMPILER=%CC% -DCMAKE_CXX_COMPILER=%CXX% -DDOM_DISALLOW_DOWNLOADS=ON -DFETCHCONTENT_FULLY_DISCONNECTED=ON -DFETCHCONTENT_UPDATES_DISCONNECTED=ON -DDOM_PLATFORM=null -DDOM_BACKEND_NULL=ON -DDOM_BACKEND_SOFT=OFF -DDOM_BACKEND_DX9=OFF" ^
  "cmake --build build/codex_verify/baseline_null_null --target dominium-launcher dominium_game" ^
  ""
if errorlevel 1 goto :summary_fail

echo.
echo ALL PASS
popd >nul
exit /b 0

:summary_fail
echo.
echo FAIL: !FAIL_STAGE! - !FAIL_NAME!
if not "!FAIL_DIR!"=="" (
  echo Build dir: !FAIL_DIR!
  echo Note: the build dir may contain partial state for inspection.
)
if not "!FAIL_CMD!"=="" (
  echo Command: !FAIL_CMD!
)
echo ONE OR MORE FAILURES
popd >nul
exit /b 1

:run_entry
set "NAME=%~1"
set "BDIR=%~2"
set "CFG=%~3"
set "BLD=%~4"
set "RUN1=%~5"
set "RUN2=%~6"
set "RUN3=%~7"
set "RUN4=%~8"

echo.
echo === %NAME% ===
echo Build dir: %BDIR%
call :run_step "configure" "%NAME%" "%BDIR%" "%CFG%"
if errorlevel 1 exit /b 1
call :run_step "build" "%NAME%" "%BDIR%" "%BLD%"
if errorlevel 1 exit /b 1
if not "%RUN1%"=="" (
  call :run_step "run: 1" "%NAME%" "%BDIR%" "%RUN1%"
  if errorlevel 1 exit /b 1
)
if not "%RUN2%"=="" (
  call :run_step "run: 2" "%NAME%" "%BDIR%" "%RUN2%"
  if errorlevel 1 exit /b 1
)
if not "%RUN3%"=="" (
  call :run_step "run: 3" "%NAME%" "%BDIR%" "%RUN3%"
  if errorlevel 1 exit /b 1
)
if not "%RUN4%"=="" (
  call :run_step "run: 4" "%NAME%" "%BDIR%" "%RUN4%"
  if errorlevel 1 exit /b 1
)
echo PASS: %NAME%
exit /b 0

:run_entry_optional
set "NAME=%~1"
set "BDIR=%~2"
set "CFG=%~3"
set "BLD=%~4"
set "RUN1=%~5"
set "RUN2=%~6"
set "RUN3=%~7"
set "RUN4=%~8"

echo.
echo === %NAME% ===
echo Build dir: %BDIR%
call :run_step_optional_configure "%NAME%" "%BDIR%" "%CFG%"
if errorlevel 1 (
  echo SKIP: configure - %NAME%
  exit /b 0
)
call :run_step "build" "%NAME%" "%BDIR%" "%BLD%"
if errorlevel 1 exit /b 1
if not "%RUN1%"=="" (
  call :run_step "run: 1" "%NAME%" "%BDIR%" "%RUN1%"
  if errorlevel 1 exit /b 1
)
if not "%RUN2%"=="" (
  call :run_step "run: 2" "%NAME%" "%BDIR%" "%RUN2%"
  if errorlevel 1 exit /b 1
)
if not "%RUN3%"=="" (
  call :run_step "run: 3" "%NAME%" "%BDIR%" "%RUN3%"
  if errorlevel 1 exit /b 1
)
if not "%RUN4%"=="" (
  call :run_step "run: 4" "%NAME%" "%BDIR%" "%RUN4%"
  if errorlevel 1 exit /b 1
)
echo PASS: %NAME%
exit /b 0

:run_step_optional_configure
set "NAME=%~1"
set "BDIR=%~2"
set "CMD=%~3"
echo CONFIGURE: %CMD%
call %CMD%
if errorlevel 1 exit /b 1
echo PASS: configure - %NAME%
exit /b 0

:run_step
set "STAGE=%~1"
set "NAME=%~2"
set "BDIR=%~3"
set "CMD=%~4"

echo %STAGE%: %CMD%
call %CMD%
if errorlevel 1 (
  echo FAIL: %STAGE% - %NAME%
  set "FAIL_NAME=%NAME%"
  set "FAIL_STAGE=%STAGE%"
  set "FAIL_DIR=%BDIR%"
  set "FAIL_CMD=%CMD%"
  exit /b 1
)
echo PASS: %STAGE% - %NAME%
exit /b 0
