@echo off
setlocal enabledelayedexpansion

set ROOT=%~dp0\..\..
for %%I in ("%ROOT%") do set ROOT=%%~fI

call "%ROOT%\scripts\setup2\check_kernel_purity.bat" || exit /b 1
call "%ROOT%\scripts\setup2\doc_lint.bat" || exit /b 1
call "%ROOT%\scripts\setup2\schema_freeze_check.bat" || exit /b 1

set REG=%ROOT%\source\dominium\setup\kernel\src\splat\dsk_splat_registry.cpp
set DOC=%ROOT%\docs\setup2\SPLAT_REGISTRY.md
set FAIL=0

for /f "delims=" %%L in ('rg -o "splat_[a-z0-9_]+" "%REG%" ^| sort /unique') do (
    findstr /c:"%%L" "%DOC%" >nul || (
        echo MISSING SPLAT DOC: %%L
        set FAIL=1
    )
)

if not "%FAIL%"=="0" exit /b 1

set BASE=%SETUP2_DOC_BASE%
if "%BASE%"=="" set BASE=HEAD~1
git rev-parse %BASE% >nul 2>&1
if errorlevel 1 goto :done

set TLV_CHANGED=0
set TLV_DOC_CHANGED=0
for /f "delims=" %%F in ('git diff --name-only %BASE% --') do (
    echo %%F | findstr /i "source/dominium/setup/kernel/include/dsk/dsk_contracts.h include/dominium/core_installed_state.h" >nul && set TLV_CHANGED=1
    echo %%F | findstr /i "docs/setup2/TLV_" >nul && set TLV_DOC_CHANGED=1
)
if "%TLV_CHANGED%"=="1" if not "%TLV_DOC_CHANGED%"=="1" (
    echo TLV schema changed without TLV docs update
    exit /b 1
)

:done
exit /b 0
