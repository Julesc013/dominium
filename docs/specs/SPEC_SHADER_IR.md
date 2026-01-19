# Shader IR Spec (Phase 1, High-Level) (REND0)

Shader IR is the single authoring surface for rendering.
Backend-specific shader sources are FORBIDDEN in game code.

## Core Rules

- Shader IR is the only authoring format.
- Backend compilation targets include HLSL, SPIR-V, and MSL.
- Backend-specific shaders MUST live under `engine/render/shader/**`.
- Game code MUST NOT reference backend shader dialects.

## Compilation Model

- Shader compilation MUST be deterministic for a given IR + RenderCaps.
- Runtime shader compilation on UI/render threads is FORBIDDEN.
- Compilation MAY occur offline or in derived-job pipelines.

## Determinism Separation

- Shader randomness is visual only and MUST NOT affect simulation.
- Shader compilation output MUST NOT be used to seed authoritative state.

## Prohibitions

- Backend-specific shader branching outside `engine/render/**` is FORBIDDEN.
- Shader model selection by user intent is FORBIDDEN.
