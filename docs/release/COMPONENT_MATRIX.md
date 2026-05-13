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

| Tier | Name |
| --- | --- |
| T0 | correctness_baseline |
| T1 | early_modern_desktop |
| T2 | broad_compatibility |
| T3 | retro_research |
| T4 | advanced_modern |
| T5 | mobile_web_exotic |

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

| Backend | Status | Tier | Notes |
| --- | --- | --- | --- |
| null | available | T0 | Null/headless verification platform. |
| posix_headless | available | T0 | UNIX default in CMake. |
| win32 | provisional | T1 | CMake accepts `win32`; Windows presets exist. |
| win32_headless | provisional | T0 | Windows headless lane. |
| cocoa | stub | T1 | Accepted by CMake; native support is not claimed. |
| posix_x11 | stub | T1 | Linux X11 lane, not implemented support. |
| posix_wayland | stub | T1 | Linux Wayland lane, not implemented support. |
| sdl2 | experimental | T1 | Dev/convenience adapter, dependency-gated. |
| android | research | T5 | Deferred mobile lane. |

## Render Backends

| Backend | Status | Tier | Notes |
| --- | --- | --- | --- |
| null | available | T0 | Correctness/headless path. |
| soft | available | T0 | Software renderer baseline. |
| gl1 | research | T3 | Fixed-function legacy lane. |
| gl2 | stub | T1 | OpenGL compatibility lane. |
| gl4 | stub | T4 | Modern OpenGL lane. |
| dx9 | research | T3 | Legacy Windows renderer lane. |
| dx11 | stub | T1 | Windows hardware renderer lane. |
| dx12 | planned | T4 | Advanced Windows lane. |
| vk1 | planned | T4 | Vulkan lane. |
| metal | planned | T4 | macOS GPU lane. |
| vector2d | planned | T2 | UI/tools/overlay acceleration lane. |

## Native Shells

| Shell | Status | Tier | Products |
| --- | --- | --- | --- |
| win32 | stub | T1 | setup, launcher, client, server |
| appkit | planned | T1 | setup, launcher, tools |
| gtk | planned | T1 | setup, launcher, tools |
| qt | research | T2 | tools |
| winforms | research | T2 | launcher, tools |
| swiftui | research | T4 | launcher, tools |
| winui3 | research | T4 | launcher, tools |

## Toolchains

| Toolchain | Status | Tier | Families |
| --- | --- | --- | --- |
| msvc | provisional | T1 | windows, winnt |
| gcc | provisional | T1 | linux, posix |
| clang | provisional | T1 | linux, macosx, posix, windows |
| xcode | planned | T1 | macosx |
| mingw | experimental | T2 | windows |
| legacy_vc6 | research | T3 | win9x, winnt |
| freestanding_16bit | research | T3 | dos, win16 |

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
