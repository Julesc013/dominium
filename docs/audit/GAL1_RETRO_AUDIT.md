Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# GAL1 Retro Audit

Date: 2026-03-13
Scope: GAL-1 compact object and hazard stub layer

## Existing Object Kind Surface

- `data/registries/object_kind_registry.json` currently declares:
  - `kind.galaxy_cell`
  - `kind.star_system`
  - `kind.star`
  - `kind.planet`
  - `kind.moon`
  - `kind.surface_tile`
  - `kind.interior_cell`
  - `kind.structure`
  - `kind.vehicle`
  - `kind.signal_node`
  - `kind.logic_network`
- No compact-object or nebula/remnant object kinds exist yet.
- Existing rows remain loadable and must not be broken by GAL-1 additions.

## Galaxy Frame Origin

- Galaxy-scale worldgen uses `frame.milky_way.galactic` from `src/worldgen/mw/mw_cell_generator.py`.
- Cell positions derive from `mw_cell_position_pc(...)` and are converted into galactic millimeter `position_ref` payloads.
- The safest stable insertion point for the central black-hole proxy is the galaxy-origin cell at GEO cell index tuple `[0, 0, 0]`.

## Existing Hazard and Field Surfaces

- GAL-0 added:
  - `field.stellar_density_proxy`
  - `field.metallicity_proxy`
  - `field.radiation_background_proxy`
  - `field.galactic_region_id`
- No `field.gravity_well_proxy` currently exists.
- Existing galaxy proxy replay/tests are pinned. GAL-1 should avoid changing GAL-0 field derivation unless an additive hook is clearly isolated.

## Current Worldgen/Object Injection Pattern

- `src/geo/worldgen/worldgen_engine.py` is the canonical non-surface worldgen seam.
- `generated_object_rows` are the authoritative spawned-object lineage surface.
- MW refiners attach additional model artifacts through deterministic `generated_*_artifact_rows`.
- `tools/xstack/sessionx/process_runtime.py` mirrors these artifact rows into runtime state and `MODEL` info artifacts.

## Safest GAL-1 Insertion Points

- Add new object kind registry rows only; do not change existing object identifiers.
- Emit compact-object stubs as additive `generated_galaxy_object_stub_artifact_rows`.
- Append GAL-1 object rows into `generated_object_rows` only when the cell deterministically emits stubs.
- Keep hazard hooks object-local in MVP default so GAL-0 field baselines do not drift silently.

## Existing UI / Lens Hooks

- GEO-5 map layers already support derived marker/orbit layers via `layer_source_payloads`.
- `layer.orbits` and telescope/admin gating in `src/geo/lens/lens_engine.py` provide the right pattern for a `layer.galaxy_objects` marker layer.
- Inspection panels already consume derived snapshot rows and can be extended without reading TruthModel directly.

## Audit Conclusion

- GAL-1 can land as an additive worldgen object-model layer plus derived map/inspect hooks.
- No runtime chemistry, catalogs, lifecycle simulation, or dynamic hazards are required.
- The highest-risk regression is accidental drift in canonical MW fixtures; GAL-1 should only alter non-origin/non-selected cells when stubs are actually emitted.
