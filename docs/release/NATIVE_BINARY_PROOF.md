# Native Binary Proof

## Status

- Phase: POST-CONVERGE-10C
- Status: partial

## Build Tuple

| Field | Value |
| --- | --- |
| tuple ID | `verify.winnt10.x64.msvc143.mt.debug` |
| toolchain | `msvc143` |
| generator | `Visual Studio 17 2022` |
| config | `debug` |
| platform | `win32` |
| renderer | `software` |
| proof level | configure; build attempted and failed at UI bind freshness gate |

## Product Binaries

| Product | Target | Executable Name | Path | Present? | Notes |
| --- | --- | --- | --- | --- | --- |
| setup | `setup_cli` | `setup` | `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug/bin/setup.exe` | yes | produced before build gate failure |
| launcher | `launcher_cli` | `launcher` | `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug/bin/launcher.exe` | yes | produced before build gate failure |
| client | `dominium_client` | `client` | `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug/bin/client.exe` | yes | produced before build gate failure |
| server | `dominium_server` | `server` | `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug/bin/server.exe` | yes | produced before build gate failure |
| tools | `dominium-tools` | `tools` | `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug/bin/tools.exe` | yes | produced before build gate failure |

## What This Proves

- The build contract, probe, local preset generator, and tuple runner exist.
- The local machine detects Visual Studio 2022/MSVC v143 and can generate the canonical local tuple preset.
- CMake configure passes for the tuple and canonical `verify` preset.
- Native product binaries are emitted locally before the build gate fails.

## What This Does Not Prove

- product boot
- runtime/session proof
- portable projection proof
- public release support
- renderer or native GUI support

## Current Blocker

Build fails after binary generation because UI bind generated outputs are stale:

- `libs/appcore/ui_bind/ui_command_binding_table.h`
- `libs/appcore/ui_bind/ui_command_binding_table.c`
- `libs/appcore/ui_bind/ui_accessibility_map.h`
- `libs/appcore/ui_bind/ui_accessibility_map.c`
- `libs/appcore/ui_bind/ui_localisation_usage_report.json`
