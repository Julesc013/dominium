@echo off
setlocal

set ROOT=%~dp0\..\..
for %%I in ("%ROOT%") do set ROOT=%%~fI
set PRESET=%1
if "%PRESET%"=="" set PRESET=msvc-debug

call "%ROOT%\scripts\setup2\maintenance_checks.bat" || exit /b 1

ctest --preset %PRESET% -L setup2 -LE setup2_adapters -E setup2_conformance^|setup2_parity_lock_^|setup2_gold_master_ --output-on-failure
if errorlevel 1 exit /b 1
ctest --preset %PRESET% -R setup2_conformance --output-on-failure
if errorlevel 1 exit /b 1
ctest --preset %PRESET% -R setup2_conformance_repeat --output-on-failure
if errorlevel 1 exit /b 1
ctest --preset %PRESET% -R setup2_parity_lock_ --output-on-failure
if errorlevel 1 exit /b 1
ctest --preset %PRESET% -R setup2_gold_master_ --output-on-failure
if errorlevel 1 exit /b 1
ctest --preset %PRESET% -L setup2_adapters --output-on-failure
exit /b %errorlevel%
