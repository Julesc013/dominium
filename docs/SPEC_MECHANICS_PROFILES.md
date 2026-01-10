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

## Related specs
- `docs/SPEC_CORE_DATA.md`
- `docs/SPEC_COSMO_CORE_DATA.md`
