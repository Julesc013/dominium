Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none

# Component Matrix

Status: PROVISIONAL

Phase: CONVERGE-11

Machine-readable source: `contracts/release/component_matrix.contract.toml`

## Purpose

This matrix records product, platform, renderer, native shell, toolchain, packaging, audio, input, network, storage, and distribution projection status. It does not implement anything.

## Status Vocabulary

Allowed statuses are `available`, `implemented`, `stub`, `planned`, `experimental`, `provisional`, `deprecated`, `unsupported`, `blocked`, `research`, and `unknown`.

`available` and `implemented` require evidence. `stub`, `planned`, and `research` rows are not support claims.

## Support Tiers

See `docs/release/SUPPORT_TIERS.md`.

| Tier | Name | Phase |
| --- | --- | --- |
| T0 | base | base |
| T1 | desktop | desktop |
| T2 | secondary | older |
| T3 | backport_research | older |
| T4 | advanced | advanced |
| T5 | mobile_web_exotic | mobile |

## POST-CONVERGE-08 Boot Evidence

Product boot proof is partial and is recorded in `docs/release/PRODUCT_BOOT_PROOF.md`.

| Product | Boot Evidence Status | Notes |
| --- | --- | --- |
| setup | blocked | no built binary; Python setup bridge fails before help under local Python 3.8 |
| launcher | partial | Python AppShell help boots; native binary not built |
| client | partial | tracked wrapper and MVP runtime entry help boot; native binary not built |
| server | partial | tracked wrapper and MVP runtime entry help boot; native binary not built |
| tools | partial | attach-console tool stub help boots; shipped tools host binary not built |

No row below is promoted to `available` or `implemented` by POST-CONVERGE-08. Planned, provisional, stub, and research statuses remain non-support claims unless later proof updates both this document and the machine-readable contract.

## POST-CONVERGE-09 Package Evidence

Package/projection smoke proof is partial and is recorded in `docs/release/PACKAGE_SMOKE_PROOF.md`.

| Area | Evidence Status | Notes |
| --- | --- | --- |
| `.dompkg` tool smoke | partial | a temporary docs package was packed and verified under `%TEMP%`, then removed |
| portable install projection | blocked | no real projection root was generated |
| package index/build manifest | blocked | no package directory or build manifest input exists |
| public release packaging | not_supported_yet | no public release artifact was generated or claimed |

This evidence does not promote packaging rows in the machine-readable contract.

## POST-CONVERGE-10 Build Evidence

Native binary proof is blocked and recorded in `docs/release/NATIVE_BINARY_PROOF.md`.

| Area | Evidence Status | Notes |
| --- | --- | --- |
| build contract | partial | tuple/floor/toolchain/artifact contracts exist |
| machine probe | partial | CMake/Python detected; no compiler/build-tool tuple available |
| generated local presets | partial | ignored preset data written with zero configure presets |
| native product binaries | blocked | no configure/build/test tuple ran |

This evidence does not promote products, toolchains, or packaging rows in the machine-readable contract.

## Products

| Product | Status | Tier | Preferred Modes | Notes |
| --- | --- | --- | --- | --- |
| client | provisional | T1 | rendered, tui, cli | Rendered game client entrypoint under `apps/client/`. |
| server | provisional | T0 | headless, tui, cli | Authoritative/headless server entrypoint under `apps/server/`. |
| launcher | provisional | T1 | os_native, tui, cli | Launch selection and preflight entrypoint under `apps/launcher/`. |
| setup | provisional | T1 | os_native, tui, cli | Install/update/repair/package setup entrypoint under `apps/setup/`. |
| tools | planned | T2 | cli, tui, os_native | Shipped product tools require classification before `apps/tools/`. |

## Product Modes

| Mode | Status | Tier | Notes |
| --- | --- | --- | --- |
| cli | available | T0 | Canonical command line surface. |
| tui | stub | T0 | TUI stubs exist; full parity is not claimed. |
| headless | available | T0 | Server, CI, and non-interactive lane. |
| rendered | provisional | T1 | Client rendered surface, backend-gated. |
| os_native | stub | T1 | Native shell stubs/surfaces exist for selected products. |

## Platform Backends

| Backend | Status | Tier | Phase | Notes |
| --- | --- | --- | --- | --- |
| null | available | T0 | base | Null/headless verification platform. |
| posix | available | T0 | base | POSIX headless/server substrate; current CMake alias is `posix_headless`. |
| win32 | provisional | T1 | desktop | Windows 7 SP1+ native platform family; includes `win32_headless` as a headless variant. |
| cocoa | stub | T1 | desktop | Mac OS X 10.9.5+ native platform family; native support is not claimed. |
| x11 | stub | T1 | desktop | First Linux desktop window lane; current CMake alias is `posix_x11`. |
| wayland | stub | T1 | desktop | Later Linux desktop window lane; current CMake alias is `posix_wayland`. |
| sdl | experimental | T1 | desktop | Dev/convenience adapter, dependency-gated; current CMake alias is `sdl2`. |

### Platform Research And Back-Port Lanes

| Lane | Status | Tier | Phase | Notes |
| --- | --- | --- | --- | --- |
| android | research | T5 | mobile | Deferred mobile lane, not first-wave desktop architecture. |

## Render Backends

| Backend | Status | Tier | Phase | Notes |
| --- | --- | --- | --- | --- |
| null | available | T0 | base | Correctness/headless path. |
| software | available | T0 | base | Software renderer baseline; current runtime/CMake alias is `soft`. |
| opengl | planned | T1 | desktop | First hardware renderer family, targeting an OpenGL 3.3 core-style shader pipeline; current transitional alias is `gl4`. |
| direct3d | planned | T1 | desktop | Windows hardware renderer family, primary version Direct3D 11. |
| metal | planned | T4 | advanced | Later Apple-native renderer, not required for the Mac OS X 10.9.5 baseline. |
| vulkan | planned | T4 | advanced | Later advanced explicit-GPU renderer; current transitional alias is `vk1`. |

### Renderer Back-Port And Advanced Lanes

| Lane | Status | Tier | Phase | Notes |
| --- | --- | --- | --- | --- |
| opengl_2_1 | research | T3 | older | Deferred compatibility/back-port lane; current CMake alias is `gl2`. |
| opengl_1_1 | research | T3 | older | Fixed-function back-port/research lane; current CMake alias is `gl1`. |
| direct3d_9 | research | T3 | older | Legacy Windows back-port/research lane; current CMake alias is `dx9`. |
| direct3d_12 | planned | T4 | advanced | Advanced Windows renderer after D3D11 and render-device contracts stabilize; current CMake alias is `dx12`. |

### Drawing Features

| Feature | Status | Tier | Phase | Notes |
| --- | --- | --- | --- | --- |
| canvas | planned | T1 | desktop | Renderer-independent 2D drawing/canvas layer implemented by renderer families; `vector2d` is a transitional alias, not a renderer backend. |

## Native Shells

| Shell | Status | Tier | Phase | Products |
| --- | --- | --- | --- | --- |
| win32 | stub | T1 | desktop | setup, launcher, client, server |
| appkit | planned | T1 | desktop | setup, launcher, tools |
| gtk | planned | T1 | desktop | setup, launcher, tools |
| qt | research | T2 | older | tools |
| winforms | research | T2 | older | launcher, tools |
| swiftui | research | T4 | advanced | launcher, tools |
| winui | research | T4 | advanced | launcher, tools |

## Toolchains

| Toolchain | Status | Tier | Phase | Families |
| --- | --- | --- | --- | --- |
| msvc | provisional | T1 | desktop | windows, winnt |
| gcc | provisional | T1 | desktop | linux, posix |
| clang | provisional | T1 | desktop | linux, macosx, posix, windows |
| xcode | planned | T1 | desktop | macosx |
| mingw | experimental | T2 | older | windows |

### Toolchain Research And Back-Port Lanes

| Lane | Status | Tier | Phase | Families |
| --- | --- | --- | --- | --- |
| legacy_vc6 | research | T3 | older | win9x, winnt |
| freestanding_16bit | research | T3 | older | dos, win16 |

## Packaging

| Package Lane | Status | Tier |
| --- | --- | --- |
| dompkg | provisional | T0 |
| portable_zip | planned | T0 |
| tarball | planned | T0 |
| app_bundle | planned | T1 |
| installer | planned | T2 |
| server_bundle | planned | T0 |
| tools_bundle | planned | T2 |
| media_offline_bundle | planned | T2 |
| symbols_debug_package | planned | T1 |
| source_archive | planned | T2 |

## Runtime Backends

| Area | Rows |
| --- | --- |
| audio | null, wasapi, directsound, coreaudio, alsa, pulseaudio, pipewire, sdl_audio |
| input | keyboard_mouse, raw_input, ime, gamepad, touch, accessibility_input |
| network | loopback, tcp, udp, reliable_udp, relay_federation, quic_webtransport |
| storage | local_fs, pack_fs, cas_store, save_export_roots, cache_staging, cloud_sync |

## Distribution Projections

The matrix references the projection model in `contracts/distribution/layout.contract.toml`. Distribution rows describe package/install/media projections, not source roots.
