Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Platform + Renderer Backends Baseline (RND-3)

Date: 2026-02-26  
Status: Baseline complete (platform layer, hardware backend minimum viable, deterministic fallback)

## 1) Platform Modules

Implemented under `src/platform/`:

1. `platform_window.py` (deterministic window state creation/resize/close)
2. `platform_input.py` (normalized keyboard/mouse events)
3. `platform_gfx.py` (backend enumeration, context creation, deterministic present events)
4. `platform_audio.py` (null audio stub)
5. `platform_input_routing.py` (RenderModel-space picking + command graph routing)
6. `__init__.py` exports canonical platform surfaces

Boundary notes:

1. Platform concerns remain presentation-only.
2. Core simulation/process runtime is not coupled to platform modules.
3. Server/tools can continue using null/software paths without native window/GPU assumptions.

## 2) Renderer Backends Implemented

Backends available in capture pipeline and CLI:

1. `null`
2. `software`
3. `hardware_gl` (minimum viable backend)

`hardware_gl` implementation details:

1. File: `src/client/render/renderers/hw_renderer_gl.py`
2. Consumes `RenderModel` only.
3. Uses platform context creation (`platform_gfx`) and deterministic present metadata.
4. Uses procedural/no-asset output path via software rasterization baseline for current minimum viable stage.

## 3) Fallback Behavior

Deterministic selection behavior:

1. Requested renderer is resolved against deterministic backend availability policy.
2. If `hardware_gl` is unavailable, resolver falls back to `software` deterministically.
3. Fallback emits run-meta event payload:
   - `event_type: render.backend_fallback`
   - requested/effective renderer IDs
   - platform ID
   - available backend list
   - reason code (`refusal.render.backend_unavailable`)
4. Fallback events are stored at deterministic derived paths under `_fallback_events/`.

## 4) Determinism Notes

1. Canonical simulation determinism remains anchored to Truth/Perceived/RenderModel and hash anchors.
2. Renderer backend choice does not affect authoritative simulation outcomes.
3. `render_model_hash` remains canonical for render input equivalence.
4. Pixel outputs are non-canonical presentation artifacts; metadata/summary hashes are deterministic for fixed inputs on the same path.

## 5) Guardrails

### RepoX invariants

1. `INV-PLATFORM-ISOLATION`
2. `INV-HW-RENDERER-RENDERMODEL-ONLY`

### AuditX analyzers

1. `E54_PLATFORM_LEAK_SMELL` (`PlatformLeakSmell`)
2. `E55_RENDERER_BACKEND_TRUTH_LEAK_SMELL` (`RendererBackendTruthLeakSmell`)

### TestX coverage

1. `testx.render.platform_layer_compiles_on_targets`
2. `testx.render.backend_selection_fallback`
3. `testx.render.renderer_truth_isolation_hardware`
4. `testx.render.renderer_truth_isolation`

## 6) Gate Execution (RND-3 Final)

1. RepoX PASS
   - `py -3 tools/xstack/repox/check.py --repo-root . --profile STRICT`
2. AuditX run
   - `py -3 tools/auditx/auditx.py scan --repo-root . --format json`
3. TestX PASS (RND-3 backend/platform subset)
   - `py -3 tools/xstack/testx/runner.py --repo-root . --profile STRICT --subset testx.render.platform_layer_compiles_on_targets,testx.render.backend_selection_fallback,testx.render.renderer_truth_isolation_hardware,testx.render.renderer_truth_isolation`
4. strict build PASS
   - `py -3 tools/setup/build.py --repo-root . --bundle bundle.base.lab --out build/dist.strict.rnd3 --cache on --format json`
5. `ui_bind --check` PASS
   - `py -3 tools/xstack/ui_bind.py --repo-root . --check`

## 7) Extension Points

1. GPU backend specialization for real OpenGL submission path.
2. Additional backends:
   - Vulkan
   - Metal
   - D3D
3. Backend capability probing and shader pipeline expansion while preserving RenderModel-only boundaries.
4. Client input routing upgrades (higher-fidelity picking and richer command graph mappings) without Truth access.
