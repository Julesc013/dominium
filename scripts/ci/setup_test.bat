@echo off
setlocal

set ROOT=%~dp0\..\..
for %%I in ("%ROOT%") do set ROOT=%%~fI
set PRESET=%1
if "%PRESET%"=="" set PRESET=msvc-debug

call "%ROOT%\scripts\setup\maintenance_checks.bat" || exit /b 1

ctest --preset %PRESET% -L setup -LE setup_adapters -E setup_conformance^|setup_parity_lock_^|setup_gold_master_ --output-on-failure
if errorlevel 1 exit /b 1
ctest --preset %PRESET% -R setup_conformance --output-on-failure
if errorlevel 1 exit /b 1
ctest --preset %PRESET% -R setup_conformance_repeat --output-on-failure
if errorlevel 1 exit /b 1
ctest --preset %PRESET% -R setup_parity_lock_ --output-on-failure
if errorlevel 1 exit /b 1
ctest --preset %PRESET% -R setup_gold_master_ --output-on-failure
if errorlevel 1 exit /b 1
ctest --preset %PRESET% -L setup_adapters --output-on-failure
exit /b %errorlevel%
