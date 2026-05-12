@echo off
setlocal enabledelayedexpansion

set ROOT=%~dp0\..\..
set TARGET=%ROOT%\source\dominium\setup\frontends\adapters

where rg >nul 2>&1
if errorlevel 1 (
  echo error: rg is required for frontend purity checks
  exit /b 1
)

set FAIL=0

call :check "setup/kernel/src" "kernel implementation includes detected in adapters"
call :check "setup/core/src" "core implementation includes detected in adapters"
call :check "setup/services/impl" "services implementation includes detected in adapters"
call :check "dsk_plan\.h" "direct plan header include detected in adapters"
call :check "dsk_jobs\.h" "direct jobs header include detected in adapters"
call :check "dsk_resume\.h" "direct resume header include detected in adapters"
call :check "dsk_(install|upgrade|repair|uninstall|verify|status)_ex" "direct kernel execution calls detected in adapters"
call :check "dsk_apply_plan" "direct plan apply calls detected in adapters"

if not "%FAIL%"=="0" exit /b 1
exit /b 0

:check
rg -n -g "*.c" -g "*.cpp" -g "*.h" -g "*.m" -g "*.mm" "%~1" "%TARGET%" >nul
if errorlevel 1 goto :eof
echo error: %~2
rg -n -g "*.c" -g "*.cpp" -g "*.h" -g "*.m" -g "*.mm" "%~1" "%TARGET%"
set FAIL=1
goto :eof
