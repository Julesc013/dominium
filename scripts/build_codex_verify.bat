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

set "FAIL=0"

call :run_entry "baseline win32 + soft" ^
  "cmake --preset baseline-debug -DDOM_DISALLOW_DOWNLOADS=ON" ^
  "cmake --build --preset baseline-debug" ^
  "build\\baseline-debug\\domino_sys_smoke.exe --smoke && build\\baseline-debug\\dgfx_demo.exe --gfx=soft --frames=120 && build\\baseline-debug\\source\\dominium\\launcher\\dominium-launcher.exe --smoke-gui --gfx=soft --profile=baseline && build\\baseline-debug\\source\\dominium\\game\\dominium_game.exe --smoke-gui --gfx=soft --profile=baseline"

call :run_entry_optional "baseline win32 + dx9 (optional)" ^
  "cmake -S . -B build/codex_verify/baseline_win32_dx9 -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_C_COMPILER=%CC% -DCMAKE_CXX_COMPILER=%CXX% -DDOM_DISALLOW_DOWNLOADS=ON -DFETCHCONTENT_FULLY_DISCONNECTED=ON -DFETCHCONTENT_UPDATES_DISCONNECTED=ON -DDOM_PLATFORM=win32 -DDOM_BACKEND_SOFT=OFF -DDOM_BACKEND_DX9=ON -DDOM_BACKEND_NULL=OFF" ^
  "cmake --build build/codex_verify/baseline_win32_dx9 --target dgfx_demo dominium-launcher dominium_game" ^
  "build\\codex_verify\\baseline_win32_dx9\\dgfx_demo.exe --gfx=dx9 --frames=120 && build\\codex_verify\\baseline_win32_dx9\\source\\dominium\\launcher\\dominium-launcher.exe --smoke-gui --gfx=dx9 --profile=baseline && build\\codex_verify\\baseline_win32_dx9\\source\\dominium\\game\\dominium_game.exe --smoke-gui --gfx=dx9 --profile=baseline"

call :run_entry "baseline win32_headless + soft" ^
  "cmake -S . -B build/codex_verify/baseline_win32_headless_soft -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_C_COMPILER=%CC% -DCMAKE_CXX_COMPILER=%CXX% -DDOM_DISALLOW_DOWNLOADS=ON -DFETCHCONTENT_FULLY_DISCONNECTED=ON -DFETCHCONTENT_UPDATES_DISCONNECTED=ON -DDOM_PLATFORM=win32_headless -DDOM_BACKEND_SOFT=ON -DDOM_BACKEND_NULL=OFF" ^
  "cmake --build build/codex_verify/baseline_win32_headless_soft --target domino_sys_smoke" ^
  "build\\codex_verify\\baseline_win32_headless_soft\\domino_sys_smoke.exe --smoke"

call :run_entry "baseline null + null" ^
  "cmake -S . -B build/codex_verify/baseline_null_null -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_C_COMPILER=%CC% -DCMAKE_CXX_COMPILER=%CXX% -DDOM_DISALLOW_DOWNLOADS=ON -DFETCHCONTENT_FULLY_DISCONNECTED=ON -DFETCHCONTENT_UPDATES_DISCONNECTED=ON -DDOM_PLATFORM=null -DDOM_BACKEND_NULL=ON -DDOM_BACKEND_SOFT=OFF -DDOM_BACKEND_DX9=OFF" ^
  "cmake --build build/codex_verify/baseline_null_null --target dominium-launcher dominium_game" ^
  ""

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
set "RUN=%~4"

echo.
echo === %NAME% ===
call %CFG%
if errorlevel 1 (
  echo FAIL: configure - !NAME!
  set "FAIL=1"
  goto :eof
)
call %BLD%
if errorlevel 1 (
  echo FAIL: build - !NAME!
  set "FAIL=1"
  goto :eof
)
if not "%RUN%"=="" (
  call %RUN%
  if errorlevel 1 (
    echo FAIL: run - !NAME!
    set "FAIL=1"
    goto :eof
  )
)
echo PASS: !NAME!
goto :eof

:run_entry_optional
set "NAME=%~1"
set "CFG=%~2"
set "BLD=%~3"
set "RUN=%~4"

echo.
echo === %NAME% ===
call %CFG%
if errorlevel 1 (
  echo SKIP: configure - !NAME!
  goto :eof
)
call %BLD%
if errorlevel 1 (
  echo FAIL: build - !NAME!
  set "FAIL=1"
  goto :eof
)
if not "%RUN%"=="" (
  call %RUN%
  if errorlevel 1 (
    echo FAIL: run - !NAME!
    set "FAIL=1"
    goto :eof
  )
)
echo PASS: !NAME!
goto :eof
