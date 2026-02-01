Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Renderer Responsibility (RENDERER-PERFECT-0)

Status: FROZEN.

Purpose: Freeze renderer behavior so rendering remains purely presentational, deterministic, and never a gameplay concern.

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

Current focus (this phase): null + software renderers are fully implemented and validated. GPU backends (DX9/DX11/DX12, VK1, GL1/GL2/GL4, Metal) are available as soft-backed stubs until their full native implementations land.

### GPU renderers (capability-gated)

- OpenGL
- Vulkan
- Direct3D (legacy + modern)
- Metal

Each GPU renderer must:

- degrade gracefully
- report capabilities explicitly
- never change semantics

### Backend stubs (capability-gated)

- GPU backends may ship as soft-backed stubs when APIs/drivers are unavailable.
- Stubs must be deterministic and presentation-only.
- Stubs must still report capabilities honestly and refuse unsupported features explicitly.
- Legacy backends (VGA/CGA/EGA/XGA, QuickDraw, GDI, etc.) may be implemented as soft-backed stubs.

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