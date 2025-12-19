@echo off
setlocal

set PRESET=%1
if "%PRESET%"=="" set PRESET=debug

cmake --preset %PRESET%
if errorlevel 1 exit /b 1

cmake --build --preset %PRESET%
if errorlevel 1 exit /b 1

ctest --preset %PRESET% --output-on-failure -R "^(dsu_|test_)"
if errorlevel 1 exit /b 1

endlocal
