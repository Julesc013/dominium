# Render Backend Matrix

Status: PROVISIONAL

Phase: CONVERGE-11

Machine-readable source: `contracts/release/component_matrix.contract.toml`

## Purpose

The render backend matrix records renderer status without implementing renderer code. It aligns CMake switches with renderer responsibility doctrine.

## Backend Status

| Backend | Status | Tier | Notes |
| --- | --- | --- | --- |
| null | available | T0 | CI/server/headless correctness path. |
| soft | available | T0 | Software renderer correctness baseline. |
| gl1 | research | T3 | Extreme legacy/fixed-function lane. |
| gl2 | stub | T1 | OpenGL compatibility lane; WGL-gated in current CMake. |
| gl4 | stub | T4 | Modern OpenGL lane. |
| dx9 | research | T3 | Legacy Windows fallback/research lane. |
| dx11 | stub | T1 | First serious Windows hardware renderer lane. |
| dx12 | planned | T4 | Advanced Windows renderer lane. |
| vk1 | planned | T4 | Vulkan renderer lane. |
| metal | planned | T4 | macOS GPU renderer lane. |
| vector2d | planned | T2 | UI/tools/overlay acceleration lane. |

## Recommended Order

1. null and soft correctness paths
2. OpenGL compatibility path
3. D3D11 Windows path
4. Metal macOS path
5. Vulkan path
6. DX9 and GL1 retro lanes
7. DX12 advanced lane
8. vector2d for UI/tools/overlay surfaces where useful

## Rules

Renderer-specific logic must not live in engine, game, product, or domain semantics.

Renderer unavailable selection must fail loudly or degrade through an explicit capability/refusal path.

GPU backend switches and interface targets are not support claims by themselves.
