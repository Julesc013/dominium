# Earth Canonical Data (CONTENT2)

Version: 1.0.0
Status: draft

## Scope
This dataset refines Earth as canonical, real-world content:
- Earth body record with tags and supported scale domains.
- Layered land and ocean surfaces.
- Atmosphere and subsurface volumes (coarse).
- Bounded region hierarchy (continents, oceans, polar regions, tectonic plates).
- Climate and biome tagging (data-only).

## Data sources
- IAU and NASA NAIF identifiers (reference tags only).
- Placeholder geometry and climate references for future imports.

## Known omissions
- Fine-grained country borders, rivers, and city catalogs.
- Detailed heightmaps or climate rasters (referenced by placeholder IDs).
- Full tectonic boundary geometry (coarse tags only).

## Extension strategy
- Add region refinement as separate files under `earth.regions/`.
- Add higher-resolution surfaces or volumes under `earth.surfaces/`.
- Apply imports via `earth.imports/` with explicit versioned datasets.

## Epistemic expectations
Earth data existence does not imply player knowledge. Discovery must flow
through sensors, reports, and observation per INF specs. Subsurface details
are not known by default.

## Validation expectations
- Files must remain schema-conforming and versioned.
- Lists must remain bounded and partitioned by scope.
- Use `tools/ci/validate_earth_data.py` for structural validation.
