Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Galaxy Compact Object Stubs

Status: Provisional
Series: GAL-1

## Purpose

GAL-1 adds deterministic, data-light galaxy object stubs so navigation, lore, and future astrophysics can reference interesting large-scale objects without introducing catalogs, gas dynamics, or stellar lifecycle simulation.

## Object Kinds

- `kind.black_hole_stub`
  - Single central supermassive black-hole proxy at the galaxy origin.
- `kind.nebula_stub`
  - Sparse procedural nebula marker for future domain packs.
- `kind.supernova_remnant_stub`
  - Sparse procedural remnant marker for future hazards and lore.

## Deterministic Placement

### Central Black Hole

- Exactly one central black-hole proxy is emitted from the galaxy-origin cell.
- Stable identity derives from:
  - universe lineage
  - origin GEO cell key
  - local subkey `galactic_center:black_hole`
- Position is the origin of `frame.milky_way.galactic`.

### Nebula / Remnant Stubs

- Placement is derived from:
  - GAL-0 density proxy
  - GAL-0 metallicity proxy
  - galactocentric radius / height
- Selection uses a named deterministic stream:
  - `rng.worldgen.galaxy_objects`
- The stream is seeded from:
  - universe seed
  - generator version
  - realism profile
  - GEO cell semantic key
  - stream name
- Generation remains bounded:
  - at most one nebula stub per eligible cell
  - at most one remnant stub per eligible cell
  - central black hole is separate and only appears in the origin cell

## Hazard Hooks

- MVP default keeps hazards object-local and static:
  - `hazard_strength_proxy`
  - optional `mass_proxy`
  - optional `radius_proxy`
- These values are inspection/view hooks only in GAL-1.
- Future ASTRO-domain packs may map them into:
  - radiation spikes
  - gravity wells
  - navigation warnings

## Map / Inspection

- `layer.galaxy_objects` is derived-only.
- Visibility follows the same diegetic telescope/admin rule family used by orbit overlays.
- Inspection panels may expose:
  - kind
  - position
  - mass proxy
  - radius proxy
  - hazard strength proxy
  - provisional replacement notes

## Stability

All GAL-1 rows are `provisional`.

- `future_series`: `ASTRO-DOMAIN`
- `replacement_target`: `dynamic lifecycle + gas dynamics`

No GAL-1 object semantics are release-frozen.

## Non-Goals

- No catalogs
- No N-body simulation
- No gas cloud simulation
- No dynamic supernova events
- No runtime black-hole gravity solver
