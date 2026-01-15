@echo off
setlocal

set BUILD_DIR=%1
if "%BUILD_DIR%"=="" set BUILD_DIR=build\debug
set VERSION=%2
if "%VERSION%"=="" set VERSION=0.1.0

set ARTIFACT_DIR=dist\artifacts\dominium-%VERSION%
set PORTABLE_OUT=dist\portable

python scripts\packaging\pipeline.py assemble --build-dir %BUILD_DIR% --out %ARTIFACT_DIR% --version %VERSION% --manifest-template assets\setup\manifests\product.template.json
if errorlevel 1 exit /b 1

python scripts\packaging\pipeline.py portable --artifact %ARTIFACT_DIR% --out %PORTABLE_OUT% --version %VERSION%
if errorlevel 1 exit /b 1

endlocal
