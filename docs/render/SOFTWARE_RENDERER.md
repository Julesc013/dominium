Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Software Renderer

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Status: normative  
Version: 1.0.0  
Scope: RND-2 CPU baseline renderer

## Purpose

Provide a cross-platform CPU renderer that consumes `RenderModel` and can run without GPU or asset packs.

## Baseline Capability

Supported primitives:

1. box
2. sphere
3. cylinder
4. capsule (approximation)
5. plane
6. line
7. glyph (minimal fallback raster)

Supported features:

1. perspective camera projection from RenderModel viewpoint
2. depth buffer
3. flat shading from procedural material base color
4. optional wireframe overlay

## Performance Expectations

1. baseline/debug renderer, not high-fidelity production path
2. deterministic metadata generation required
3. bounded per-frame CPU work by resolution and renderable count

## Determinism Guarantees

Guaranteed deterministic:

1. summary metadata structure
2. counts/fingerprints/hashes based on RenderModel ordering
3. snapshot metadata fields

Pixel output disclaimer:

1. exact pixel hashes may vary across architectures/platforms
2. canonical truth determinism uses `render_model_hash` and deterministic summaries
3. `pixel_hash` is informational unless compared in same platform lane

## Isolation and Asset Policy

Forbidden:

1. TruthModel access
2. simulation mutation
3. required texture/sound assets

Software renderer must produce useful output with primitive + procedural material data only.
