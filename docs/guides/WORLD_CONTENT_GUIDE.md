# WORLD_CONTENT_GUIDE - World Data Authoring (CONTENT2)

Status: draft
Version: 2

## Purpose
Define how canonical world data is authored and organized under `data/world/`
without embedding gameplay mechanics or simulation logic.

## Authoring format
- Use JSON or TOML authoring files that map directly to `schema/world/*`.
- Keep each file independently loadable and bounded.
- Include `schema_id`, `schema_version`, and a migration stub placeholder.

## Directory layout
Recommended structure:
- `data/world/<world_id>/`
  - `*.system.*` for system records
  - `*.orbits.*` for orbital rails
  - `bodies/`, `moons/`, `belts/` for celestial bodies
  - `*.surfaces.*` for surfaces and regions
  - `earth/` for detailed Earth partitions (surfaces, regions, climate, imports)
  - `milky_way/` for galactic structure, anchors, and procedural rules

## Determinism and performance
- No file may include unbounded lists.
- Ordering in lists must be deterministic and stable.
- No per-tick updates or physics simulation encoded in content.

## Epistemic boundary
Data existence does not imply player knowledge. Visibility and discovery must
flow through sensors, reports, and communications per INF specs.

## Validation
Run the Sol dataset validator:
```
python tools/ci/validate_sol_data.py --repo-root=.
```
This is a structural check only; it does not apply gameplay logic.

Run the Earth dataset validator:
```
python tools/ci/validate_earth_data.py --repo-root=.
```

Run the Milky Way dataset validator:
```
python tools/ci/validate_milky_way_data.py --repo-root=.
```
