@echo off
setlocal

set ROOT=%~dp0\..\..
for %%I in ("%ROOT%") do set ROOT=%%~fI
set PRESET=%1
if "%PRESET%"=="" set PRESET=msvc-debug

cmake --build --preset %PRESET% --target dominium-setup2 setup2_kernel_tests setup2_services_fs_tests setup2_services_platform_tests setup2_kernel_services_tests setup2_splat_tests setup2_plan_tests setup2_apply_tests setup2_cli_golden_tests setup2_parity_lock_tests setup2_gold_master_tests setup2_conformance_runner setup2_conformance_repeat_tests setup2_adapter_steam_tests setup2_adapter_macos_pkg_tests setup2_adapter_linux_wrappers_tests setup2_adapter_wrapper_tests setup2_adapter_windows_tests setup2-adapters
exit /b %errorlevel%
