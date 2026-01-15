@echo off
setlocal

set TARGET=%~1
set BUILD_DIR=%~2

if "%TARGET%"=="" set TARGET=all
if "%BUILD_DIR%"=="" set BUILD_DIR=%CD%\build\msvc-debug

set ROOT=%~dp0\..\..
set LEGACY_SRC=%ROOT%\source\dominium\setup\installers\windows_legacy
set OUT_DIR=%ROOT%\dist\legacy\windows

if /I "%TARGET%"=="win9x" goto build_win9x
if /I "%TARGET%"=="dos" goto build_dos
if /I "%TARGET%"=="win16" goto build_win16
if /I "%TARGET%"=="all" goto build_all

echo Unknown target: %TARGET%
echo Valid: dos ^| win16 ^| win9x ^| all
exit /b 1

:build_all
call "%~f0" win9x "%BUILD_DIR%"
call "%~f0" dos "%BUILD_DIR%"
call "%~f0" win16 "%BUILD_DIR%"
exit /b 0

:build_win9x
echo Building Win9x installer via CMake target legacy_win9x_installer
cmake --build "%BUILD_DIR%" --target legacy_win9x_installer
exit /b %ERRORLEVEL%

:build_dos
if "%WATCOM%"=="" (
  echo WATCOM not set. Install OpenWatcom and set WATCOM to the root path.
  exit /b 1
)
if not exist "%OUT_DIR%" mkdir "%OUT_DIR%"
set WCL=%WATCOM%\binw\wcl.exe
if not exist "%WCL%" set WCL=%WATCOM%\binnt\wcl.exe
if not exist "%WCL%" (
  echo wcl.exe not found in %WATCOM%.
  exit /b 1
)
echo Building DOS installer (INSTALL.EXE)...
"%WCL%" -bt=dos -fe="%OUT_DIR%\INSTALL.EXE" ^
  "%LEGACY_SRC%\dos\src\dos_main.c" ^
  "%LEGACY_SRC%\dos\src\dos_tui.c" ^
  "%LEGACY_SRC%\dos\src\dos_extract.c" ^
  "%LEGACY_SRC%\legacy_core\src\legacy_fs_dos.c" ^
  "%LEGACY_SRC%\legacy_core\src\legacy_invocation.c" ^
  "%LEGACY_SRC%\legacy_core\src\legacy_log.c" ^
  "%LEGACY_SRC%\legacy_core\src\legacy_manifest.c" ^
  "%LEGACY_SRC%\legacy_core\src\legacy_state.c" ^
  "%LEGACY_SRC%\legacy_core\src\legacy_txn.c" ^
  "%LEGACY_SRC%\legacy_core\src\legacy_uninstall.c" ^
  "%LEGACY_SRC%\legacy_core\src\legacy_verify.c"
exit /b %ERRORLEVEL%

:build_win16
if "%WATCOM%"=="" (
  echo WATCOM not set. Install OpenWatcom and set WATCOM to the root path.
  exit /b 1
)
if not exist "%OUT_DIR%" mkdir "%OUT_DIR%"
set WCL=%WATCOM%\binw\wcl.exe
set WRC=%WATCOM%\binw\wrc.exe
if not exist "%WCL%" set WCL=%WATCOM%\binnt\wcl.exe
if not exist "%WRC%" set WRC=%WATCOM%\binnt\wrc.exe
if not exist "%WCL%" (
  echo wcl.exe not found in %WATCOM%.
  exit /b 1
)
if not exist "%WRC%" (
  echo wrc.exe not found in %WATCOM%.
  exit /b 1
)
echo Building Win16 installer (SETUP.EXE)...
"%WRC%" -r -fo="%OUT_DIR%\win16_resources.res" "%LEGACY_SRC%\win16\src\win16_resources.rc"
"%WCL%" -bt=windows -fe="%OUT_DIR%\SETUP.EXE" ^
  "%LEGACY_SRC%\win16\src\win16_main.c" ^
  "%LEGACY_SRC%\win16\src\win16_gui.c" ^
  "%OUT_DIR%\win16_resources.res" ^
  "%LEGACY_SRC%\legacy_core\src\legacy_fs_win16.c" ^
  "%LEGACY_SRC%\legacy_core\src\legacy_invocation.c" ^
  "%LEGACY_SRC%\legacy_core\src\legacy_log.c" ^
  "%LEGACY_SRC%\legacy_core\src\legacy_manifest.c" ^
  "%LEGACY_SRC%\legacy_core\src\legacy_state.c" ^
  "%LEGACY_SRC%\legacy_core\src\legacy_txn.c" ^
  "%LEGACY_SRC%\legacy_core\src\legacy_uninstall.c" ^
  "%LEGACY_SRC%\legacy_core\src\legacy_verify.c"
exit /b %ERRORLEVEL%
