Status: DERIVED
Last Reviewed: 2026-02-13
Supersedes: none
Superseded By: none

# Survival Vertical Slice

This document describes the current minimal deterministic survival baseline implemented through schemas and registries.

## Scope

The slice is intentionally minimal and structural:

- deterministic need decay and hazard response
- basic gather/craft/shelter/consume loop contracts
- death and persistence constraints
- profile-driven softcore vs hardcore deltas
- diegetic-only survival lens enforcement

Primary source:

- `data/registries/survival_vertical_slice.json`
- `schema/survival/survival_vertical_slice.schema`

## Minimal Gameplay Survival Model

Survival behavior is defined through profile + law + parameters, not hardcoded mode flags:

- experience: `exp.survival` (`data/registries/experience_profiles.json`)
- law (softcore): `law.survival.softcore` (`data/registries/law_profiles.json`)
- law (hardcore): `law.survival.hardcore`
- parameter bundles: `survival.params.default`, `survival.params.harsh` (`data/registries/parameter_bundles.json`)

## Needs Model

Agent fields tracked in the vertical slice:

- `need.energy`
- `need.hydration`
- `need.exposure`
- `health.hp`
- `status.alive`

See: `data/registries/survival_vertical_slice.json` (`agent_fields`).

## Hazard Model

World fields feeding survival pressure:

- `env.temperature`
- `env.daylight`

Hazard/needs update processes:

- `process.need_tick`
- `process.exposure_tick`

See:

- `data/registries/survival_vertical_slice.json`
- `data/registries/process_requirements.json`

## Resource Gathering

Minimal gather contract:

- process: `process.gather_resource`
- material affordance requirements: declared in `data/registries/process_requirements.json`
- baseline materials: `mat.wood`, `mat.stone`, `mat.water`, `mat.leaves` (`data/registries/materials.json`)

## Crafting Basics

Minimal crafting contract:

- process: `process.craft_basic_tool`
- tool capabilities:
  - `toolcap.sharp_edge_grade1`
  - `toolcap.blunt_force_grade1`

References:

- `data/registries/tool_capabilities.json`
- `data/registries/process_requirements.json`

## Shelter and Survival

Shelter is represented as:

- assembly: `assembly.shelter_basic`
- shelter field: `shelter.rating`
- process: `process.build_shelter`

Shelter effects are parameterized through bundle values such as:

- `exposure.shelter_multiplier`
- `exposure.daylight_multiplier`

Values live in:

- `survival.params.default`
- `survival.params.harsh`

## Death and Persistence

Death transition process:

- `process.death_process`

Persistence behavior is law-driven:

- softcore (`law.survival.softcore`): `persistence.respawn.allowed`
- hardcore (`law.survival.hardcore`): `persistence.respawn.forbidden`

No extra hardcoded hardcore branch is required when profile bindings are respected.

## Deterministic Baseline

Determinism is guaranteed by:

- explicit process IDs and process requirements
- parameter bundles with deterministic numeric values
- law/experience/profile registry selection
- governance checks in RepoX/TestX/AuditX

Related enforcement/tests are tracked through:

- `data/registries/testx_suites.json`
- `tests/invariant/`
- `tests/integration/`

## Survival Default Lens Model (Diegetic)

Survival law enforces diegetic lens constraints:

- allowed: `lens.diegetic.*`
- forbidden: `lens.nondiegetic.*`

Lens definitions:

- `data/registries/lenses.json`
- `schema/lens/lens.schema`

Survival profile implications:

- no non-diegetic console
- no debug overlay lens
- no freecam lens

Observer profile (`exp.observer`) intentionally differs and allows non-diegetic lenses under explicit entitlements.

## Related Docs

- Architecture summary: `docs/ARCHITECTURE.md`
- Governance stack: `docs/XSTACK.md`
- Canon glossary: `docs/GLOSSARY.md`
