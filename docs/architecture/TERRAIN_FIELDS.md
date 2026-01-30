# Terrain Field Stack (TERRAIN0)

Status: binding.
Scope: minimum canonical terrain/matter field stack.

All fields:
- are provider-resolved and composable.
- are LOD-aware and budgeted.
- are unit-tagged per `docs/architecture/UNIT_SYSTEM_POLICY.md`.
- support unknown/latent states (epistemics).
- are read-only outside Process execution.

## Required fields

| Field | Type | Unit | Notes |
| --- | --- | --- | --- |
| `terrain.phi` | SDF | `unit.length.meter` | Signed distance field boundary. |
| `terrain.material_primary` | categorical id | `unit.dimensionless.ratio` | Primary material id (unitless placeholder). |
| `terrain.support_capacity` | field | `unit.pressure.pascal` | Support envelope for stability checks. |
| `env.temperature` | field | `unit.temperature.kelvin` | Environmental temperature. |
| `env.moisture` | field | `unit.dimensionless.ratio` | Moisture ratio (0..1). |
| `terrain.roughness` | field | `unit.dimensionless.ratio` | Micro-roughness envelope. |
| `travel.cost` | field | `unit.dimensionless.ratio` | Normalized travel cost weight. |

## Optional / extensible fields
- `terrain.strata_layers`
- `env.wind`
- `env.precipitation`
- `eco.vegetation_density`
- `eco.nutrients`
- `hazard.radiation`
- `magic.mana_density`
- `infra.density`

Optional fields are unit-tagged, LOD-aware, and provider-resolved using the
same rules as required fields.
