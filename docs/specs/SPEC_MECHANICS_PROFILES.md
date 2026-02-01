Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. Engine provides generic primitives only if referenced.

GAME:
- Rules, policy, and interpretation defined by this spec.
- Implementation lives under `game/` (rules/content/ui as applicable).

TOOLS:
- Authoring/inspection utilities described here.
- Implementation lives under `tools/` (including shared tool runtime).

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
# SPEC_MECHANICS_PROFILES — Mechanics-First Overlays

Status: draft  
Version: 1

## Purpose
Mechanics profiles provide deterministic, sim-affecting modifiers that shape
gameplay without encoding physics equations. Profiles are authored in core data
and compiled into TLV packs.

## SYSTEM_MECHANICS_PROFILE (sim-affecting)
Example fields (all sim-affecting):
- `navigation_instability_factor`
- `debris_collision_modifier`
- `radiation_baseline`
- `supernova_timer_ticks` (optional)
- `warp_cap_modifier`
- `survey_difficulty`

## SITE_MECHANICS_PROFILE (sim-affecting)
Example fields:
- `hazard_radiation`
- `hazard_pressure`
- `corrosion_rate`
- `resource_yield_modifiers`
- `access_constraints`

## Rules
- Every mechanics profile MUST change at least one decision-relevant variable.
- Profiles are composable; composition order MUST be deterministic.
- Profiles MUST NOT encode physics equations; they provide modifiers only.
- Sim-affecting fields MUST be included in identity digests.

## On-disk TLV record definitions (coredata pack)
Records are emitted as a TLV stream of records where each record is
`u32_le type_id` + `u32_le len` + payload bytes. Each record payload is a TLV
stream of fields (`u32_le tag` + `u32_le len` + payload bytes; little-endian).

Record type IDs (u32, stable):
- `MECH_SYSTEM_PROFILE`: `0x00020001`
- `MECH_SITE_PROFILE`: `0x00020002`

Record schema version: `1` (implicit in the pack; recorded in the manifest).

### MECH_SYSTEM_PROFILE payload (TLV)
Tags:
- `1`: `id` (string, UTF-8)
- `2`: `id_hash` (u64_le; FNV-1a of `id`)
- `3`: `navigation_instability_q16` (i32_le; Q16.16)
- `4`: `debris_collision_q16` (i32_le; Q16.16)
- `5`: `radiation_baseline_q16` (i32_le; Q16.16)
- `6`: `warp_cap_modifier_q16` (i32_le; Q16.16)
- `7`: `survey_difficulty_q16` (i32_le; Q16.16)
- `8`: `supernova_timer_ticks` (u64_le, optional)

### MECH_SITE_PROFILE payload (TLV)
Tags:
- `1`: `id` (string, UTF-8)
- `2`: `id_hash` (u64_le; FNV-1a of `id`)
- `3`: `hazard_radiation_q16` (i32_le; Q16.16)
- `4`: `hazard_pressure_q16` (i32_le; Q16.16)
- `5`: `corrosion_rate_q16` (i32_le; Q16.16)
- `6`: `temperature_extreme_q16` (i32_le; Q16.16)
- `7`: `resource_yield` (container, repeated; tags below)
- `8`: `access_constraint` (string, repeated)

Resource yield container tags (for 7):
- `1`: `resource_id` (string)
- `2`: `modifier_q16` (i32_le; Q16.16)

## Related specs
- `docs/specs/SPEC_CORE_DATA.md`
- `docs/specs/SPEC_COSMO_CORE_DATA.md`