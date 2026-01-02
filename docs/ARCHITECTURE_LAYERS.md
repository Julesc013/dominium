# Architecture Layers

This repo enforces a strict layering model for launcher/setup so kernel logic
cannot accidentally depend on OS/UI/platform code.

## Layer Model
Layer A: KERNEL
- Pure logic/state machines. No OS headers, no UI headers, no platform libs.
- Depends only on core_* shared libs and API facades (headers only).

Layer B: SERVICES
- Side effects behind facades (filesystem, process, time, network).
- Platform-agnostic API headers in services_api; implementations live in services_impl_*.

Layer C: PROVIDERS
- Optional external integrations behind provider_api + query_interface.
- Selected by registry/solver later; R-1 uses stubs only.

Layer D: FRONTENDS
- GUI/TUI/CLI entrypoints. Can depend on DUI/DTUI/terminal APIs.
- Must not reach into kernel internals beyond published APIs.

Layer E: PLATFORM BACKENDS
- Win32/Cocoa/GTK/etc implementations behind facades.
- OS headers and platform libs only live here.

## Canonical Modules (Current)
Common:
- core_tlv, core_audit, core_util, core_err (INTERFACE targets)
- provider_api (INTERFACE), providers_builtin (STATIC)
- dui_api (INTERFACE)

Launcher:
- launcher_kernel (ALIAS of dominium_launcher_core)
- launcher_services_api (INTERFACE)
- launcher_services_impl_instances (STATIC)
- launcher_services_impl_null (STATIC)
- launcher_frontend_cli, launcher_frontend_tui, launcher_frontend_gui (STATIC)

Setup:
- setup_kernel (ALIAS of dsu_core)
- setup_services_api (INTERFACE)
- setup_services_impl_platform, setup_services_impl_null (STATIC)
- setup_frontend_cli (INTERFACE), setup_frontend_gui (STATIC)
- setup_adapters_platform_* (STATIC)

## Allowed Dependencies (Summary)
Kernel -> core_* + *_services_api only
Services impl -> kernel + platform libs (OS headers ok here)
Providers impl -> provider_api (plus platform libs if needed)
Frontends -> kernel + services_api + DUI/DTUI/terminal APIs
Platform backends -> services_impl + platform libs only

## How to Add New Code
New kernel logic:
1) Place sources under kernel directories.
2) Link only core_* targets (no platform libs).
3) Keep headers in include/ and avoid OS/UI includes.

New platform backend:
1) Implement in services_impl_* or adapters_platform_*.
2) Add OS includes only in the backend target.
3) Do not add platform include dirs to kernel targets.

New facade/API:
1) Use abi_version + struct_size + query_interface (see docs/SPEC_ABI_TEMPLATES.md).
2) Add an INTERFACE target for headers.
3) Provide a null implementation for headless tests if needed.

## Mechanical Gates
Layer checks:
- scripts/check_layers.py (forbidden includes in kernel sources)
- CMake link guard in source/dominium/CMakeLists.txt (kernel may only link core_* libs)

Tests:
- launcher_kernel_smoke
- setup_kernel_smoke
- dominium_layer_checks (ctest wrapper for scripts/check_layers.py)

Local runs:
- scripts/test_kernel.bat
- scripts/test_all.bat
