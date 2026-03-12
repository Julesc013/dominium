Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

## GEO-5 Retro-Consistency Audit

Date: 2026-03-09
Scope: projection, lens, map/minimap, render, CCTV-style remote views

### Canon and invariant context

- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- GEO-0..4 constitutions and baseline audits
- Render truth isolation and epistemic gating invariants already active in RepoX/TestX

### Existing camera and freecam hooks

- `src/control/view/view_engine.py`
  - Canonical view-policy binding already exists for first-person, third-person, freecam, spectator, and replay modes.
  - View policy negotiation is authority- and entitlement-gated, but it does not yet produce topology-aware projected cell artifacts.
- `tools/xstack/sessionx/observation.py`
  - Observation derives `camera_viewpoint` and lens-scoped `channels`.
  - Camera state is already filtered through law and epistemic policy before PerceivedModel is emitted.
  - This is the correct insertion point for future projected-view requests, but GEO-5 can remain derived-only without mutating observation flow.
- `src/client/render/renderers/software_renderer.py`
  - Existing renderer calls `geo_project(...)` per renderable for perspective projection.
  - This is object-centric render projection, not map/minimap/cell-selection projection.
  - It remains RenderModel-only and should stay separate from GEO-5 projected-view artifacts.

### Existing map and minimap behavior

- `src/diegetics/instrument_kernel.py`
  - `instrument.map_local` already produces a deterministic, memory-backed local map readout.
  - Current output is a list of discovered entries, not a canonical projected cell artifact.
- `src/client/render/render_model_adapter.py`
  - Diegetic instrument overlays render labels such as compass, clock, and map counts.
  - These overlays are UI glyphs, not geometry-aware maps or atlas unwraps.
- `tools/dgfx_demo/dgfx_demo.c`
  - Contains a standalone minimap demo path.
  - This is presentation/demo code, not the canonical simulation-side projection contract.

### Existing truth and perceived boundaries

- `tools/xstack/sessionx/observation.py`
  - Truth-to-Perceived derivation is already canonical and deterministic.
  - Perceived payloads carry `truth_overlay` only when epistemically allowed.
- `src/client/render/render_model_adapter.py`
  - RenderModel is correctly derived from PerceivedModel only.
- `tools/xstack/sessionx/ui_host.py`
  - The UI host still accepts `universe_state` for executing window actions through SessionX.
  - This is not a render read path, but it is the main remaining UI-facing truth dependency worth tightening later.
  - GEO-5 should avoid extending this pattern; new view adapters must consume projected view artifacts only.

### Existing direct view/data assumptions that GEO-5 should absorb

- Perspective projection is currently treated as a low-level object projection call rather than a first-class projection request over cell selections.
- Diegetic map output is memory-entry based and not bound to projection profiles or view types.
- There is no single derived artifact for:
  - ortho map cells
  - minimap cells
  - atlas unwrap tiles
  - slice views
  - CCTV snapshot tiles

### Migration notes

- Map/minimap overlays should migrate toward `projected_view_artifact` generation instead of bespoke UI overlays.
- Any future atlas or slice UI should request:
  - `ProjectionRequest`
  - `LensRequest`
  - lawful perceived layer sources
- CCTV-style remote views should route through SIG-carried observation artifacts, not direct camera/truth reads.
- `tools/xstack/sessionx/ui_host.py` should eventually stop requiring raw `universe_state` in its public adapter boundary and instead consume intent-capable service inputs plus derived view artifacts.

### Audit conclusion

- Existing truth isolation in render is solid enough for GEO-5.
- The missing contract is not basic camera law-gating; it is the absence of a canonical, deterministic projected-view artifact that bridges GEO, epistemics, and presentation.
- GEO-5 should introduce that artifact and keep adapters derived-only.
