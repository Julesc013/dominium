# Sol System Canonical Data (CONTENT1)

Version: 1.0.0
Status: draft

## Scope
This dataset instantiates the Sol star system as data only:
- Sun, eight planets, and major moons.
- Asteroid belt, Kuiper belt, and Oort cloud as belt bodies.
- Deterministic orbital rails with ACT-based periods.
- Surfaces and regions for Earth, Mars, and the Moon.

## Encoding
- Files are JSON authoring units intended to map to `schema/world/*`.
- Each file includes `schema_id`, `schema_version`, and a `migration_stub`.
- No gameplay logic or simulation rules are embedded.

## ACT timebase note
`sol.orbits.json` uses `act_unit = "hour"` as an authoring convention.
This does not redefine ACT; it is a content scaling note only.

## Known omissions
- Minor moons, dwarf planets, and small-body catalogs are omitted.
- Detailed region geometry and heightmaps are referenced by ID only.
- Atmosphere and climate data are tagged, not simulated.

## Epistemic expectations
World data existence does not imply player knowledge. Discovery should flow
through sensors, reports, and observation as defined in INF specs.

## Scaling and loading
- Each file is independently loadable and bounded.
- No file requires full-universe loading.
- Lists are intentionally short; future expansions must partition by body.

## Extending this dataset
- Add additional moons under `sol.moons/` with matching orbital rails.
- Add regions and surfaces by extending `sol.surfaces.json`.
- Keep IDs stable; add new IDs rather than renaming existing ones.

## Validation expectations
- Files must remain schema-conforming and versioned.
- New fields require a MINOR or MAJOR version bump with migration notes.
- Use `tools/ci/validate_sol_data.py` to run basic structural checks.
