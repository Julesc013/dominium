@echo off
setlocal enabledelayedexpansion

set ROOT=%~dp0..
set ROOT=%ROOT%\..
pushd "%ROOT%" >nul

set KERNEL_DIR=source\dominium\setup\kernel
set FAIL=0

for %%H in (windows.h unistd.h sys/stat.h sys/types.h sys/wait.h) do (
    for /f "delims=" %%F in ('findstr /s /n /i /c:"%%H" "%KERNEL_DIR%\*.c" "%KERNEL_DIR%\*.cpp" "%KERNEL_DIR%\*.h" 2^>nul') do (
        echo %%F | findstr /i /c:"dsk_forbidden_includes.h" >nul
        if errorlevel 1 (
            echo Forbidden header %%H referenced: %%F
            set FAIL=1
        )
    )
)

popd >nul
if %FAIL% neq 0 exit /b 1
exit /b 0
