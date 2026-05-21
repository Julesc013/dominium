Status: CANONICAL
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Renderer Responsibility (RENDERER-PERFECT-0)

Status: FROZEN.

Purpose: Freeze renderer behavior so rendering remains purely presentational, deterministic, and never a gameplay concern.

CONVERGE-11 cross-reference: renderer support posture is recorded in `contracts/release/component_matrix.contract.toml` and `docs/release/RENDER_BACKEND_MATRIX.md`. This document remains the renderer responsibility contract; the matrix does not implement render backends.

## Renderer Responsibility (Final)

Renderers MUST:

- consume immutable snapshots
- consume signal/field visualizations
- render UI declaratively
- respect capability queries (client.ui.* only)
- function with zero assets

Renderers MUST NOT:

- mutate state
- run simulation logic
- affect timing
- perform authority checks

## Required Renderer Backends

All backends expose identical abstract interfaces and identical UI semantics.

### Null renderer

- produces no visual output
- exercises the full render pipeline
- used for CI, servers, verification

### Software renderer

- CPU-only
- deterministic output
- vector / ASCII / simple raster
- zero GPU assumptions

Current focus: null and software renderers are the correctness floor. First-wave hardware renderer planning is shader-based: OpenGL targets a 3.3 core-style shader pipeline, and Direct3D targets version 11. Metal, Vulkan, and Direct3D 12 are later advanced lanes. OpenGL 2.1, OpenGL 1.1, and Direct3D 9 remain back-port/research lanes and must not shape first-wave renderer architecture.

### GPU renderers (capability-gated)

- OpenGL
- Direct3D 11
- Metal
- Vulkan

Each GPU renderer must:

- degrade gracefully
- report capabilities explicitly
- never change semantics

### Backend stubs (capability-gated)

- GPU backends may ship as soft-backed stubs when APIs/drivers are unavailable.
- Stubs must be deterministic and presentation-only.
- Stubs must still report capabilities honestly and refuse unsupported features explicitly.
- Legacy backends (OpenGL 2.1, OpenGL 1.1, Direct3D 9, VGA/CGA/EGA/XGA, QuickDraw, GDI, etc.) may be implemented as soft-backed stubs or research adapters only when explicitly scoped.

### Bare‑metal / minimal renderer

- framebuffer-only
- text‑mode / low‑res graphics
- legacy hardware support

## UI & Presentation Model

- UI is declarative and data-driven.
- UI packs affect presentation only.
- Identical UI semantics across renderers.

## Asset Handling

- Renderer works with zero assets.
- Procedural or fallback visuals exist.
- Missing assets never crash the renderer.
- Asset resolution is renderer-agnostic.

## Signal & Field Visualization

Supported visualization types:

- scalar fields
- vector fields
- signal streams

Visualization is:

- non-authoritative
- sampled
- deterministic

## Performance & Scaling

- Rendering batches deterministically.
- Render cost scales with visible data only.
- Renderers do not traverse the entire world.
- Renderers respect collapse/expand boundaries.

## Freeze & Lock

The renderer layer is FROZEN. Allowed changes are limited to:

- new backends
- bug fixes
- performance optimizations that preserve invariants
