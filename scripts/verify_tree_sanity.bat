@echo off
setlocal enabledelayedexpansion

set "fail=0"

call :check_dir "engine\\launcher_core_launcher"
call :check_dir "engine\\setup_core_setup"
call :check_dir "engine\\include\\dominium"
call :check_dir "engine\\include\\dsu"
call :check_dir "engine\\include\\dsk"
call :check_dir "engine\\include\\dui"
call :check_dir "engine\\source"

if "%fail%"=="0" (
  echo Tree sanity OK.
  exit /b 0
)

echo Tree sanity FAILED.
exit /b 1

:check_dir
if exist "%~1" (
  echo Forbidden path exists: %~1
  set "fail=1"
)
exit /b 0
