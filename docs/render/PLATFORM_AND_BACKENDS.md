Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Platform And Backends

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Status: normative  
Version: 1.0.0  
Scope: RND-3 platform abstraction and hardware backend boundaries

## 1) Platform Layer Responsibilities

The platform layer (`src/platform/`) owns presentation/runtime OS integration only:

1. Window lifecycle
   1. create window
   2. resize notifications
   3. destroy window
2. Input capture
   1. keyboard/mouse events
   2. normalized platform input events
3. Graphics surface management
   1. graphics context/surface creation
   2. frame presentation (swap/present)
4. Audio surface
   1. optional stub by default
   2. no simulation coupling

Timing in the platform layer is presentation-only and never authoritative for simulation outcomes.

## 2) Renderer Backends

Supported renderer classes:

1. `null` renderer
   1. deterministic metadata artifacts
   2. no pixel output
2. `software` renderer
   1. CPU fallback
   2. no external assets required
3. `hardware_gl` renderer (optional)
   1. consumes `RenderModel` only
   2. platform `gfx` context/surface usage

If a requested hardware backend is unavailable, deterministic fallback to software renderer is required with a run-meta event.

## 3) Strict Boundaries

Hard constraints:

1. Engine/core simulation does not import platform modules.
2. Hardware backend modules must not import TruthModel or process runtime mutation surfaces.
3. Backends consume only `RenderModel` + platform presentation adapters.
4. Removing hardware renderer modules must not affect simulation semantics.
5. Render pixel bytes are derived artifacts; canonical determinism is anchored to `RenderModel` hash and deterministic summaries.

## 4) Portability Targets

Target host operating systems:

1. Windows
2. macOS
3. Linux

Portability contract:

1. platform modules isolate host-specific details
2. software renderer remains usable everywhere
3. null renderer remains available for server/CI/headless flows
