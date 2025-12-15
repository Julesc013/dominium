@echo off
setlocal EnableExtensions EnableDelayedExpansion

rem Codex verification skeleton (Prompt 3).
rem - Configures and builds a small build matrix in isolated build dirs.
rem - No downloads (DOM_DISALLOW_DOWNLOADS=ON).

set "ROOT=%~dp0.."
pushd "%ROOT%" >nul

set "PATH=C:\msys64\ucrt64\bin;%PATH%"

set "CC=C:/msys64/ucrt64/bin/cc.exe"
set "CXX=C:/msys64/ucrt64/bin/c++.exe"

set "FAIL=0"

call :run_entry "baseline win32 + soft" ^
  "cmake --preset baseline-debug" ^
  "cmake --build --preset baseline-debug"

call :run_entry "baseline win32_headless + soft" ^
  "cmake -S . -B build/codex_verify/baseline_win32_headless_soft -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_C_COMPILER=%CC% -DCMAKE_CXX_COMPILER=%CXX% -DDOM_DISALLOW_DOWNLOADS=ON -DDOM_PLATFORM=null -DDOM_BACKEND_SOFT=ON -DDOM_BACKEND_NULL=OFF" ^
  "cmake --build build/codex_verify/baseline_win32_headless_soft --target dominium-launcher"

call :run_entry "baseline null + null" ^
  "cmake -S . -B build/codex_verify/baseline_null_null -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_C_COMPILER=%CC% -DCMAKE_CXX_COMPILER=%CXX% -DDOM_DISALLOW_DOWNLOADS=ON -DDOM_PLATFORM=null -DDOM_BACKEND_NULL=ON -DDOM_BACKEND_SOFT=OFF" ^
  "cmake --build build/codex_verify/baseline_null_null --target dominium-launcher"

echo.
if "%FAIL%"=="0" (
  echo ALL PASS
  popd >nul
  exit /b 0
)

echo ONE OR MORE FAILURES
popd >nul
exit /b 1

:run_entry
set "NAME=%~1"
set "CFG=%~2"
set "BLD=%~3"

echo.
echo === %NAME% ===
call %CFG%
if errorlevel 1 (
  echo FAIL: configure - %NAME%
  set "FAIL=1"
  goto :eof
)
call %BLD%
if errorlevel 1 (
  echo FAIL: build - %NAME%
  set "FAIL=1"
  goto :eof
)
echo PASS: %NAME%
goto :eof
