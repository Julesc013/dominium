@echo off
setlocal enabledelayedexpansion

set ROOT=%~dp0\..\..
for %%I in ("%ROOT%") do set ROOT=%%~fI
set PRESET=%1
if "%PRESET%"=="" set PRESET=msvc-debug

set LOG_DIR=%ROOT%\dist\release\setup2_release_gate
set LOG_DIR_REL=dist/release/setup2_release_gate
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

set BUILD_LOG=%LOG_DIR%\build.log
set MAINT_LOG=%LOG_DIR%\maintenance.log
set UNIT_LOG=%LOG_DIR%\unit_tests.log
set PARITY_LOG=%LOG_DIR%\parity_lock.log
set GOLD_LOG=%LOG_DIR%\gold_master.log
set CONF_LOG=%LOG_DIR%\conformance.log
set ADAPTER_LOG=%LOG_DIR%\adapter_checks.log
set PACK_LOG=%LOG_DIR%\packaging_checks.log

set BUILD_STATUS=pass
set MAINT_STATUS=pass
set UNIT_STATUS=pass
set PARITY_STATUS=pass
set GOLD_STATUS=pass
set CONF_STATUS=pass
set ADAPTER_STATUS=pass
set PACK_STATUS=pass

> "%BUILD_LOG%" echo ^>^> cmake --build --preset %PRESET% --target dominium-setup2 setup2_kernel_tests setup2_services_fs_tests setup2_services_platform_tests setup2_kernel_services_tests setup2_splat_tests setup2_plan_tests setup2_apply_tests setup2_cli_golden_tests setup2_parity_lock_tests setup2_gold_master_tests setup2_conformance_runner setup2_conformance_repeat_tests setup2_adapter_steam_tests setup2_adapter_macos_pkg_tests setup2_adapter_linux_wrappers_tests setup2_adapter_wrapper_tests setup2_adapter_windows_tests setup2-adapters
cmake --build --preset %PRESET% --target dominium-setup2 setup2_kernel_tests setup2_services_fs_tests setup2_services_platform_tests setup2_kernel_services_tests setup2_splat_tests setup2_plan_tests setup2_apply_tests setup2_cli_golden_tests setup2_parity_lock_tests setup2_gold_master_tests setup2_conformance_runner setup2_conformance_repeat_tests setup2_adapter_steam_tests setup2_adapter_macos_pkg_tests setup2_adapter_linux_wrappers_tests setup2_adapter_wrapper_tests setup2_adapter_windows_tests setup2-adapters >> "%BUILD_LOG%" 2>&1
if errorlevel 1 set BUILD_STATUS=fail

> "%MAINT_LOG%" echo ^>^> scripts\\setup2\\maintenance_checks.bat
call "%ROOT%\\scripts\\setup2\\maintenance_checks.bat" >> "%MAINT_LOG%" 2>&1
if errorlevel 1 set MAINT_STATUS=fail

> "%UNIT_LOG%" echo ^>^> ctest --preset %PRESET% -L setup2 -LE setup2_adapters -E setup2_conformance^|setup2_parity_lock_^|setup2_gold_master_ --output-on-failure
ctest --preset %PRESET% -L setup2 -LE setup2_adapters -E setup2_conformance^|setup2_parity_lock_^|setup2_gold_master_ --output-on-failure >> "%UNIT_LOG%" 2>&1
if errorlevel 1 set UNIT_STATUS=fail

> "%PARITY_LOG%" echo ^>^> ctest --preset %PRESET% -R setup2_parity_lock_ --output-on-failure
ctest --preset %PRESET% -R setup2_parity_lock_ --output-on-failure >> "%PARITY_LOG%" 2>&1
if errorlevel 1 set PARITY_STATUS=fail

> "%GOLD_LOG%" echo ^>^> ctest --preset %PRESET% -R setup2_gold_master_ --output-on-failure
ctest --preset %PRESET% -R setup2_gold_master_ --output-on-failure >> "%GOLD_LOG%" 2>&1
if errorlevel 1 set GOLD_STATUS=fail

> "%CONF_LOG%" echo ^>^> ctest --preset %PRESET% -R setup2_conformance --output-on-failure
ctest --preset %PRESET% -R setup2_conformance --output-on-failure >> "%CONF_LOG%" 2>&1
if errorlevel 1 set CONF_STATUS=fail
>> "%CONF_LOG%" echo ^>^> ctest --preset %PRESET% -R setup2_conformance_repeat --output-on-failure
ctest --preset %PRESET% -R setup2_conformance_repeat --output-on-failure >> "%CONF_LOG%" 2>&1
if errorlevel 1 set CONF_STATUS=fail

> "%ADAPTER_LOG%" echo ^>^> ctest --preset %PRESET% -R setup2_adapter_steam --output-on-failure
ctest --preset %PRESET% -R setup2_adapter_steam --output-on-failure >> "%ADAPTER_LOG%" 2>&1
if errorlevel 1 set ADAPTER_STATUS=fail
>> "%ADAPTER_LOG%" echo ^>^> ctest --preset %PRESET% -R setup2_adapter_windows_exe --output-on-failure
ctest --preset %PRESET% -R setup2_adapter_windows_exe --output-on-failure >> "%ADAPTER_LOG%" 2>&1
if errorlevel 1 set ADAPTER_STATUS=fail

> "%PACK_LOG%" echo ^>^> ctest --preset %PRESET% -R setup2_adapter_wrapper_scripts --output-on-failure
ctest --preset %PRESET% -R setup2_adapter_wrapper_scripts --output-on-failure >> "%PACK_LOG%" 2>&1
if errorlevel 1 set PACK_STATUS=fail
>> "%PACK_LOG%" echo ^>^> ctest --preset %PRESET% -R setup2_adapter_macos_pkg --output-on-failure
ctest --preset %PRESET% -R setup2_adapter_macos_pkg --output-on-failure >> "%PACK_LOG%" 2>&1
if errorlevel 1 set PACK_STATUS=fail
>> "%PACK_LOG%" echo ^>^> ctest --preset %PRESET% -R setup2_adapter_linux_wrappers --output-on-failure
ctest --preset %PRESET% -R setup2_adapter_linux_wrappers --output-on-failure >> "%PACK_LOG%" 2>&1
if errorlevel 1 set PACK_STATUS=fail

set OVERALL=pass
if not "%BUILD_STATUS%"=="pass" set OVERALL=fail
if not "%MAINT_STATUS%"=="pass" set OVERALL=fail
if not "%UNIT_STATUS%"=="pass" set OVERALL=fail
if not "%PARITY_STATUS%"=="pass" set OVERALL=fail
if not "%GOLD_STATUS%"=="pass" set OVERALL=fail
if not "%CONF_STATUS%"=="pass" set OVERALL=fail
if not "%ADAPTER_STATUS%"=="pass" set OVERALL=fail
if not "%PACK_STATUS%"=="pass" set OVERALL=fail

set SUMMARY=%ROOT%\dist\release\setup2_release_gate_summary.json
(
echo {
echo   "schema_version":"setup2-release-gate-1",
echo   "log_dir":"%LOG_DIR_REL%",
echo   "stages":[
echo     {"name":"build","status":"%BUILD_STATUS%","log":"%LOG_DIR_REL%/build.log"},
echo     {"name":"maintenance_checks","status":"%MAINT_STATUS%","log":"%LOG_DIR_REL%/maintenance.log"},
echo     {"name":"unit_tests","status":"%UNIT_STATUS%","log":"%LOG_DIR_REL%/unit_tests.log"},
echo     {"name":"parity_lock","status":"%PARITY_STATUS%","log":"%LOG_DIR_REL%/parity_lock.log"},
echo     {"name":"gold_master","status":"%GOLD_STATUS%","log":"%LOG_DIR_REL%/gold_master.log"},
echo     {"name":"conformance","status":"%CONF_STATUS%","log":"%LOG_DIR_REL%/conformance.log"},
echo     {"name":"adapter_checks","status":"%ADAPTER_STATUS%","log":"%LOG_DIR_REL%/adapter_checks.log"},
echo     {"name":"packaging_checks","status":"%PACK_STATUS%","log":"%LOG_DIR_REL%/packaging_checks.log"}
echo   ],
echo   "overall":"%OVERALL%"
echo }
) > "%SUMMARY%"

if not "%OVERALL%"=="pass" exit /b 1
exit /b 0
