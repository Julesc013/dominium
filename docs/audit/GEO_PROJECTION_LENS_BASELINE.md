Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# GEO Projection & Lens Baseline

Status: GEO-5 baseline complete.
Scope: deterministic projection requests, epistemic-gated lens derivation, UI adapters, CCTV SIG delivery hook, proof/replay, and enforcement.

## Projection Profiles Supported

- `geo.projection.ortho_2d`
  Deterministic bounded cell-window projection for map and minimap views over GEO partitions.
- `geo.projection.atlas_unwrap_stub`
  Deterministic atlas/tile projection for `geo.topology.sphere_surface_s2` and atlas-backed partitions.
- `geo.projection.slice_nd_stub`
  Deterministic slice projection stub for higher-dimensional charts and hyperplane selection.
- Torus and periodic map support
  Projection enumeration respects topology/partition context, so wrapped spaces remain portable without UI-side coordinate hacks.
- CCTV remote view
  Uses canonical projection requests plus SIG-derived snapshot delivery rather than direct renderer access.

## Lens Layers

- `layer.terrain_stub`
  Terrain or atlas-terrain data sourced from lawful perceived map instrument readings or explicit lawful terrain entries.
- `layer.temperature`
  Field-backed temperature sampling routed through GEO-bound field storage and deterministic field sampling.
- `layer.pollution`
  Field-backed pollution sampling through lawful layer payloads and GEO field cell keys.
- `layer.infrastructure_stub`
  Overlay markers sourced from entitled infrastructure/process artifacts only.
- `layer.entity_markers_stub`
  Entity marker overlays sourced from epistemically lawful known-entity rows only.

## Epistemic Gating Rules

- All views are derived from `ProjectionRequest + LensRequest + PerceivedModel`, never from direct TruthModel reads in UI adapters.
- Terrain presentation in diegetic lenses requires a map instrument channel or explicit omniscient debug entitlement.
- Infrastructure and entity overlays enforce declared channel and entitlement requirements per layer source payload.
- Unknown or disallowed data is redacted to `hidden` with deterministic `hidden_reason` values.
- Diegetic scalar layers apply deterministic quantization through lens request policy, preserving replayable coarse readouts.
- Omniscient debug access is allowed only when `allow_omniscient_debug` is explicitly requested, the lens is debug-like, and authority entitlements permit it.
- CCTV views are derived observations transported through SIG channel/envelope/receipt artifacts with deterministic delay.

## Proof, Replay, and Cache Surfaces

- Projection/lens/view registries now contribute:
  - `projection_profile_registry_hash`
  - `lens_layer_registry_hash`
  - `view_type_registry_hash`
- Control proof GEO identity extensions include the new registry hashes when present.
- Server-authoritative and SRZ proof surfaces propagate the same registry hashes into mobility/control proof bundles.
- `tools/geo/tool_replay_view_window.py` regenerates canonical projected views and verifies stable fingerprints across repeated runs.
- Derived view caching is keyed by deterministic projection request, lens request, truth hash anchor, epistemic policy, and registry surfaces.

## Validation Summary

- RepoX STRICT: pass
- AuditX STRICT: pass, `promoted_blockers=0`
- GEO-5 TestX subset: pass
- `tool_replay_view_window.py`: pass
  `deterministic_fingerprint = 69207b2ebf263d0d835ee8d9da9a240ce6374219bb2ab203961bf658ffe8cce0`
- strict build: pass
  `canonical_content_hash = 9cdabc6762b207303ef749adddf995b3fe64fe1d0605241cf417330f1966e2b5`
- topology map regenerated
  `deterministic_fingerprint = c76580655394888ed9bd5c2acc664d526d81eb816ae033592ec9fe780b1e1eed`

## Readiness for GEO-6

- Canonical projection requests now yield deterministic projected cell windows over portable topology/partition profiles.
- Lens derivation is explicitly observer/perception-gated, which keeps future pathing/traversal UIs from depending on truth leaks.
- UI surfaces are reduced to derived artifacts and buffers, so GEO-6 traversal/path views can build on the same projection/lens contract without special renderer authority.
