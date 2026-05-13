# Native Binary Proof

## Status

- Phase: POST-CONVERGE-10B
- Status: blocked

## Build Tuple

| Field | Value |
| --- | --- |
| tuple ID | `verify.winnt10.x64.msvc143.mt.debug` |
| toolchain | `msvc143` |
| generator | `Visual Studio 17 2022` |
| config | `debug` |
| platform | `win32` |
| renderer | `software` |
| proof level | detected; configure attempted and failed during CMake generation |

## Product Binaries

| Product | Target | Executable Name | Path | Present? | Notes |
| --- | --- | --- | --- | --- | --- |
| setup | `setup_cli` | `setup` | `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug/bin` | no | configure failed |
| launcher | `launcher_cli` | `launcher` | `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug/bin` | no | configure failed |
| client | `dominium_client` | `client` | `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug/bin` | no | configure failed |
| server | `dominium_server` | `server` | `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug/bin` | no | configure failed |
| tools | `dominium-tools` | `tools` | `.dominium.local/build/tuple.verify.winnt10.x64.msvc143.mt.debug/bin` | no | configure failed |

## What This Proves

- The build contract, probe, local preset generator, and tuple runner exist.
- The local machine now detects Visual Studio 2022/MSVC v143 and can generate the canonical local tuple preset.
- CMake reaches compiler and Windows SDK selection.
- Native binaries remain missing.

## What This Does Not Prove

- product boot
- runtime/session proof
- portable projection proof
- public release support
- renderer or native GUI support

## Current Blocker

CMake generation fails before build files are complete because test CMake files still reference retired root paths:

- `client/presentation/frame_graph_builder.cpp`
- `server/authority/dom_server_authority.cpp`
