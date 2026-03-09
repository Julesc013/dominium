Status: DERIVED
Last Reviewed: 2026-03-09
Supersedes: none
Superseded By: none

# MVP Viewer Baseline

## Scope

UX-0 seals the MVP viewer shell for Dominium v0.0.0.

The shell provides:

- deterministic session start with `profile.bundle.mvp_default`
- seed entry and runtime bootstrap wiring
- freecam/body lens switching under profile gating
- teleport flows for Sol, Earth, random-star, object-id, and coordinate targets
- inspection panels for celestial objects, tiles, geometry, fields, logic/network, and system/capsule summaries
- overlay provenance via the canonical GEO-9 property-origin explain tool
- GEO-5 map/minimap views for CLI/TUI/GUI without texture/model dependencies

## User Flows

- Launch:
  - Boot -> BundleSelect -> SeedSelect -> SessionRunning
  - the canonical bundle and pack lock are loaded through the MVP runtime bootstrap
- Teleport:
  - `/tp sol` and `/tp earth` route through the deterministic Sol anchor
  - `/tp random_star` selects a candidate via `rng.ui.teleport.random_star`
  - object-id and coordinate teleports remain process-only camera plans
- Lens switching:
  - `lens.fp`, `lens.tp`, `lens.freecam`, and `lens.inspect` resolve through embodiment lens profiles
  - nondiegetic lens changes remain entitlement-gated

## Inspection Surfaces

- Object inspector exposes:
  - `object_id`
  - object kind/type
  - parent relationship
  - key physical/orbital parameters
  - current refinement/LOD state
- Field inspector exposes:
  - temperature
  - daylight
  - pollution
- Overlay provenance exposes:
  - tool id `tool.geo.explain_property_origin`
  - explain contract ids
  - current layer id
  - prior value chain

Inspection consumes snapshots, derived overlays, and explain-tool outputs only.

## Map And Redaction

- Map view uses GEO projection requests plus lens requests.
- Minimap is a bounded ROI subset keyed by the same truth anchor hash cache policy.
- CLI/TUI prefer ASCII projection output; GUI prefers buffer output.
- Diegetic redaction remains active:
  - map layers can hide behind `map_instrument_required`
  - marker layers can hide behind `channel_required`
  - privileged overlays can hide behind `entitlement_required`

## Budget And Caching

- map/minimap resolution degrades deterministically from compute budgets
- debug view surfaces throttle deterministically by compute profile
- projected view artifacts cache by truth anchor hash plus semantic request inputs

## Readiness

UX-0 is ready for:

- DIST-series packaging/bootstrap wiring
- MVP traversal across galaxy -> Sol -> Earth without loading-screen semantics
- later tool/interaction expansion on top of the lawful viewer shell
