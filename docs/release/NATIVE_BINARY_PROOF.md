# Native Binary Proof

## Status

- Phase: POST-CONVERGE-10E
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
| proof level | build; focused AuditX CTest fixed; full CTest blocked by unit/RepoX gates |

## Product Binaries

| Product | Target | Executable Name | Path | Present? | Notes |
| --- | --- | --- | --- | --- | --- |
| setup | `setup_cli` | `setup` | `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug/bin/setup.exe` | yes | tuple build passes |
| launcher | `launcher_cli` | `launcher` | `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug/bin/launcher.exe` | yes | tuple build passes |
| client | `dominium_client` | `client` | `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug/bin/client.exe` | yes | tuple build passes |
| server | `dominium_server` | `server` | `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug/bin/server.exe` | yes | tuple build passes |
| tools | `dominium-tools` | `tools` | `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug/bin/tools.exe` | yes | tuple build passes |

## What This Proves

- The build contract, probe, local preset generator, and tuple runner exist.
- The local machine detects Visual Studio 2022/MSVC v143 and can generate the canonical local tuple preset.
- CMake configure passes for the tuple and canonical `verify` preset.
- The VS2022/v143 tuple build passes and emits native product binaries.
- The canonical `verify` build passes and bounded product smoke checks pass.
- Focused AuditX CTest cases pass after targeted path and generated-projection fixes.

## What This Does Not Prove

- product boot
- runtime/session proof
- portable projection proof
- public release support
- renderer or native GUI support

## Current Blocker

CTest remains blocked after build proof:

- full tuple CTest timed out after 20 minutes; CTest reached `invariant_units_present`, which fails on undeclared `unit.mass_energy.stub` and `unit.schema`
- canonical `ctest --preset verify --output-on-failure` exceeded a 40-minute shell timeout; focused logs show `inv_repox_rules` fails on broad RepoX drift while AuditX cases now pass
- no generated binaries were committed
