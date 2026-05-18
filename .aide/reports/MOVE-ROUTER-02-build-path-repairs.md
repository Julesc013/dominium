# MOVE-ROUTER-02 Build Path Repairs

Status: PARTIAL
Generated: 2026-05-18

## Repairs Applied

- Updated top-level CMake to add `cmake/legacy_libs` instead of old `libs`.
- Promoted DOM contracts CMake ownership to `contracts/abi/dom_contracts`.
- Promoted build identity ownership to `runtime/build_identity`.
- Promoted Win32 UI backend ownership to `runtime/shell/ui_backends/win32`.
- Updated ABI include consumers to `contracts/abi/dom_contracts/include`.
- Updated UI bind generated include/output paths to `runtime/shell/appcore/ui_bind`.
- Updated build graph lock registry paths for the promoted CMake and ABI surfaces.
- Updated `.gitattributes` for the routed UI bind generated path.

## Remaining Build/Test Path Work

The build reached the integrated test phase, but broader TestX still contains
old path assumptions. These belong to MOVE-ROUTER-02R.
