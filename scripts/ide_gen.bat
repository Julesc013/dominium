@echo off
setlocal enabledelayedexpansion

if "%~1"=="" (
  echo usage: ide_gen.bat ^<preset^> [preset...]
  exit /b 2
)

for %%P in (%*) do (
  echo [ide_gen] configure %%P
  cmake --preset %%P
  if errorlevel 1 exit /b 1
  set "manifest=ide\\manifests\\%%P.projection.json"
  if exist "!manifest!" (
    echo [ide_gen] manifest: !manifest!
  ) else (
    echo [ide_gen] manifest missing: !manifest!
  )
)
