Status: DERIVED
Last Reviewed: 2026-03-09
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# SOL0 Retro Audit

## Scope

This audit records the repository state before SOL-0 Sol pin-pack work.

Audit targets:

- MW-2 star, planet, and moon identity derivation
- GEO-9 property-patch overlay contract
- deterministic Sol targeting strategy
- current mismatch between procedural MW output and a minimal official Sol overlay

## Existing MW Identity Derivation

Current MW identity law is already deterministic and overlay-safe.

Relevant runtime surfaces:

- `src/worldgen/mw/mw_cell_generator.py`
  - star-system local subkeys are `star_system:<local_index>`
  - system object IDs are derived through `geo_object_id(...)`
- `src/worldgen/mw/mw_system_refiner_l2.py`
  - primary star local subkey is `system:<system_object_id>:star:0`
  - planet local subkey is `system:<system_object_id>:planet:<planet_index>`
  - moon stub local subkey is `system:<system_object_id>:moon:<planet_index>:<moon_index>`
- `src/geo/index/object_id_engine.py`
  - final `object_id_hash` is derived from:
    - `universe_identity_hash`
    - canonical `geo_cell_key`
    - `object_kind_id`
    - `local_subkey`

Audit conclusion:

- SOL-0 must not replace MW identity derivation.
- The lawful Sol integration path is to target the existing GEO/MW identity lineage, not to special-case object IDs.

## Existing GEO-9 Overlay Patch Contract

The overlay system already supports the kind of official patching SOL-0 needs.

Relevant surfaces:

- `schema/geo/property_patch.schema`
  - requires `target_object_id`
  - requires canonical `property_path`
  - forbids identity replacement through property patches
- `src/geo/overlay/overlay_merge_engine.py`
  - `build_property_patch(...)`
  - `build_default_overlay_manifest(...)`
  - `merge_overlay_view(...)`
  - official layers require trusted `signature_status`

Current overlay semantics:

- base procedural layer remains canonical
- official overlays may override properties
- immutable identity paths are blocked
- missing objects may be added only through explicit overlay rows, not by replacing base identity

Audit conclusion:

- SOL-0 can ship as an official overlay pack using GEO-9 property patches.
- The pack must avoid delete or identity-replacement behavior.

## Existing Sol Targeting State

There is currently no lawful deterministic Sol anchor in the active MW generator.

Findings:

- `src/worldgen/mw/mw_cell_generator.py`
  - currently treats every Milky Way cell purely as a density/prior outcome
  - does not reserve a deterministic Sol anchor cell
- `data/registries/realism_profile_registry.json`
  - default realism profile has no `sol_anchor_cell_key` or equivalent routing hint
- `data/world/milky_way/milky_way.anchors.json`
  - contains legacy/stub Sol anchor naming, but it is not connected to current MW worldgen identity generation
- `packs/domain/astronomy.sol/pack.json`
  - exists as a legacy astronomy/domain pack surface, not as the MVP official overlay pack requested here

Audit conclusion:

- SOL-0 needs an explicit deterministic Sol anchor route in active MW/runtime data.
- The most stable path is an anchor cell key declared by the realism profile and consumed by the MW cell generator.

## Current Procedural-versus-Pinned Mismatch

Current procedural MW output does not yet guarantee that a specific system can be treated as Sol.

Mismatch details:

- there is no guaranteed system at any fixed galactic cell
- there is no current binding from a procedural star-system ID to the official Sol hierarchy
- there is no active pack under `packs/official/pack.sol.pin_minimal/`
- the MVP dist/runtime bundle currently references a Sol pack alias only

Consequence:

- a minimal official Sol overlay cannot yet target live procedural object IDs without an anchor rule
- Luna pinning is also unresolved, because MW-2 moon stubs are probabilistic rather than explicitly routed to a Sol lineage

Audit conclusion:

- SOL-0 must add a deterministic anchor rule before official property patches can be authoritative.
- Earth and Luna should be treated as stable overlay slots on the anchored Sol lineage rather than as free-floating named bodies.

## Reusable Surfaces

Useful existing surfaces are already present:

- `tools/mvp/runtime_bundle.py`
  - canonical MVP bundle and pack-lock wiring
- `tools/xstack/testx/tests/geo8_testlib.py`
  - deterministic worldgen identity fixture pattern
- `tools/xstack/testx/tests/geo9_testlib.py`
  - official overlay merge and identity-stability fixture pattern
- `src/geo/overlay/overlay_merge_engine.py`
  - official pack trust enforcement and deterministic merge ordering

Audit conclusion:

- SOL-0 can be implemented by combining the existing MW identity law, GEO-9 overlay merge path, and MVP bundle surfaces.
- No catalog import path or eager solar-system data bootstrap is required.
