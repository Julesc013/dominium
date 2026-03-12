Status: DERIVED
Last Reviewed: 2026-03-09
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# UX0 Retro Audit

## Scope

Audit of existing client, renderer, inspection, and projection/runtime surfaces before implementing the UX-0 MVP viewer shell.

## Existing Client UI Scaffolding

- Legacy/native shell paths already exist under `client/shell/`, `client/core/`, `client/presentation/`, and `client/ui/workspaces/`.
- The current deterministic Python-side headless UI surface is `tools/xstack/sessionx/ui_host.py`.
- `tools/xstack/sessionx/ui_host.py` already provides:
  - deterministic window gating by lens and entitlements
  - headless window action dispatch
  - deterministic search-result injection into PerceivedModel navigation surfaces
- There is no Python `src/client/ui/` viewer-shell package yet; UX-0 can be added without colliding with an established Python viewer-shell implementation.

## Existing Render Backends

- Deterministic render adapter exists at `src/client/render/render_model_adapter.py`.
- Deterministic render backends already exist:
  - `src/client/render/renderers/null_renderer.py`
  - `src/client/render/renderers/software_renderer.py`
  - `src/client/render/renderers/hw_renderer_gl.py`
- Existing documentation already treats null/software/hardware as presentation-only backends:
  - `docs/app/CLIENT_RENDERER_UI.md`
  - `docs/build/CI_MATRIX.md`
- Render surfaces already consume RenderModel only and do not require textures/models for baseline output.

## Existing Inspect / Provenance Surfaces

- Authoritative inspection snapshot generation already exists through `process.inspect_generate_snapshot` in `tools/xstack/sessionx/process_runtime.py`.
- Derived inspection overlay generation already exists in `src/client/interaction/inspection_overlays.py`.
- GEO-9 overlay provenance is already exposed through `tools/geo/tool_explain_property_origin.py`.
- Existing redaction and inspection determinism coverage already exists in TestX:
  - `test_lens_redaction_policy_applied`
  - `test_property_origin_tool_correct`
  - `test_ranked_restricts_admin_panels`

## Existing Projection / Map Surfaces

- GEO-5 projection request and cell enumeration exist in `src/geo/projection/projection_engine.py`.
- GEO-5 lens/view artifact derivation exists in `src/geo/lens/lens_engine.py`.
- Current map/minimap relevant view types already exist in `data/registries/view_type_registry.json`:
  - `view.map_ortho`
  - `view.minimap`
  - `view.atlas_unwrap`
- Existing map redaction rules already enforce diegetic and entitlement gating at the projected-view layer.

## Existing Teleport / Lens / Session Bootstrap Surfaces

- MVP bootstrap already exists in:
  - `tools/mvp/runtime_bundle.py`
  - `tools/mvp/runtime_entry.py`
- Existing teleport and lens processes already exist in `tools/xstack/sessionx/process_runtime.py`:
  - `process.camera_teleport`
  - `process.camera_set_view_mode`
  - `process.camera_set_lens`
  - `process.control_set_view_lens`
  - `process.worldgen_request`
- Milky Way query and teleport planning already exists in `src/worldgen/mw/system_query_engine.py`.
- EMB-0 lens authorization and camera transforms already exist in `src/embodiment/lens/lens_engine.py`.

## Truth-Leak Risks

- `tools/xstack/sessionx/ui_host.py` currently accepts `universe_state` for action execution. That is acceptable for existing headless tooling, but UX-0 must not introduce new viewer-shell reads from TruthModel or direct authoritative state.
- `tools/xstack/sessionx/observation.py` legitimately reads truth because it is the Observation Kernel. UX-0 viewer code must consume its PerceivedModel outputs only.
- `src/client/interaction/preview_generator.py` and `src/client/interaction/inspection_overlays.py` may consume `truth_overlay.state_hash_anchor`; that is acceptable because the anchor is already an epistemically gated derived field, not direct truth access.
- New UX-0 modules must not import or depend on:
  - `build_truth_model`
  - `observe_truth`
  - raw `universe_state`
  - direct process runtime mutation helpers

## Platform / Asset Assumptions

- No asset dependency is required for current render/model/view surfaces.
- Existing runtime/bootstrap is already portable across CLI, GUI, and headless entrypoints.
- Existing renderer docs already declare a null-renderer/headless path and software-renderer path for cross-platform use.

## Reuse Decisions

- Reuse `tools/mvp/runtime_bundle.py` for canonical bundle/session bootstrap.
- Reuse `src/embodiment/lens/lens_engine.py` for profile-gated lens resolution and camera-state derivation.
- Reuse `src/worldgen/mw/system_query_engine.py` and Sol anchor helpers for teleport/query planning.
- Reuse `src/geo/projection/projection_engine.py` and `src/geo/lens/lens_engine.py` for map/minimap generation.
- Reuse `src/client/interaction/inspection_overlays.py` and `tools/geo/tool_explain_property_origin.py` for inspect/provenance surfaces.

## UX-0 Implementation Constraint

- The new viewer shell must be a lens-first, derived-artifact adapter layer.
- It must not become a second observation kernel, second truth model, or ad hoc process runtime.
