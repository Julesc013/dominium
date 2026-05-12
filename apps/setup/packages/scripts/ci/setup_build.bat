@echo off
setlocal

set ROOT=%~dp0\..\..
for %%I in ("%ROOT%") do set ROOT=%%~fI
set PRESET=%1
if "%PRESET%"=="" set PRESET=msvc-debug

cmake --build --preset %PRESET% --target dominium-setup setup_kernel_tests setup_services_fs_tests setup_services_platform_tests setup_kernel_services_tests setup_splat_tests setup_plan_tests setup_apply_tests setup_cli_golden_tests setup_parity_lock_tests setup_gold_master_tests setup_conformance_runner setup_conformance_repeat_tests setup_adapter_steam_tests setup_adapter_macos_pkg_tests setup_adapter_linux_wrappers_tests setup_adapter_wrapper_tests setup_adapter_windows_tests setup-adapters
exit /b %errorlevel%
