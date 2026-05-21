Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none

# Render Backend Matrix

Status: PROVISIONAL

Phase: CONVERGE-11

Machine-readable source: `contracts/release/component_matrix.contract.toml`

## Purpose

The render backend matrix records renderer status without implementing renderer code. Renderer identities are release-facing families; current CMake/API-version switches remain transitional aliases or research lanes until runtime naming is reviewed explicitly.

## Backend Status

| Backend | Status | Tier | Phase | Target | Notes |
| --- | --- | --- | --- | --- | --- |
| null | available | T0 | base | headless | CI/server/headless correctness path. |
| software | available | T0 | base | CPU raster | Software renderer correctness baseline; runtime/CMake alias: `soft`. |
| opengl | planned | T1 | desktop | 3.3 core shader pipeline | First cross-platform hardware renderer family; current transitional alias is `gl4`. |
| direct3d | planned | T1 | desktop | Direct3D 11 | Windows hardware renderer family; current transitional alias: `dx11`. |
| metal | planned | T4 | advanced | later Apple-native renderer | Not required for the Mac OS X 10.9.5 baseline. |
| vulkan | planned | T4 | advanced | later explicit-GPU renderer | Advanced lane after base renderer contracts stabilize; current transitional alias: `vk1`. |

## Back-Port And Advanced Lanes

| Lane | Status | Tier | Phase | Notes |
| --- | --- | --- | --- | --- |
| opengl_2_1 | research | T3 | older | Deferred compatibility/back-port lane; current CMake alias: `gl2`. |
| opengl_1_1 | research | T3 | older | Fixed-function research lane; current CMake alias: `gl1`. |
| direct3d_9 | research | T3 | older | Legacy Windows back-port/research lane; current CMake alias: `dx9`. |
| direct3d_12 | planned | T4 | advanced | Advanced Windows lane after Direct3D 11 and render-device contracts stabilize; current CMake alias: `dx12`. |

## Drawing Features

| Feature | Status | Tier | Phase | Notes |
| --- | --- | --- | --- | --- |
| canvas | planned | T1 | desktop | Renderer-independent 2D/canvas drawing feature implemented by `software`, `opengl`, `direct3d`, `metal`, and `vulkan`. `vector2d` is a transitional alias, not a renderer backend. |

## Recommended Order

1. null correctness path
2. software renderer plus canvas drawing
3. OpenGL renderer, target 3.3 shader pipeline
4. Direct3D renderer, primary version 11
5. Metal later Apple-native lane
6. Vulkan later advanced lane
7. Direct3D 12 advanced Windows lane
8. OpenGL 2.1, OpenGL 1.1, and Direct3D 9 back-port/research lanes

## Rules

Renderer-specific logic must not live in engine, game, product, or domain semantics.

Renderer unavailable selection must fail loudly or degrade through an explicit capability/refusal path.

GPU backend switches and interface targets are not support claims by themselves.

Fixed-function and immediate-mode renderer designs must not shape first-wave renderer architecture. They may remain research or debug experiments only when explicitly scoped.
