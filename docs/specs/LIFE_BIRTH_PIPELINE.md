# LIFE Birth Pipeline (LIFE3)

This guide describes the deterministic birth pipeline, gestation scheduling,
and lineage recording implemented in LIFE3.

## Pipeline summary

1) Validate parents, resources, and authority
2) Create GestationState and schedule completion via ACT due scheduler
3) On completion:
   - create Person (and Body if micro-active)
   - append BirthEvent
   - record lineage
   - update cohort counts (macro mode only)
4) Emit audit log entry and optional epistemic notice

All steps are deterministic and replay-safe.

## Key modules

- `game/include/dominium/life/birth_pipeline.h`
  - `life_request_birth(...)` entrypoint
  - `life_birth_scheduler_*` scheduling functions
- `game/include/dominium/life/gestation_state.h`
  - GestationState registry
- `game/include/dominium/life/birth_event.h`
  - BirthEvent records (append-only)
- `game/include/dominium/life/lineage.h`
  - Lineage records per person
- `game/include/dominium/life/cohort_update_hooks.h`
  - Cohort aggregation hooks

## Determinism and ordering

- Parent IDs are sorted deterministically before scheduling.
- Gestation uses ACT ticks only and is scheduled via `dg_due_scheduler`.
- Lineage records store parent IDs and certainty deterministically.

## Resource and authority checks

- `game/rules/reproduction_rules.*` bounds parent counts and gestation timing.
- `game/rules/needs_constraints.*` enforces minimal food/shelter constraints.
- Authority checks require explicit control authority for known parents.

## Cohort integration

- Macro births update cohort counts only when micro fidelity is inactive.
- Micro births create persons/bodies without modifying cohort counts.
- This avoids double counting while preserving macro invariants.

## Epistemic boundary

- Birth events are authoritative; knowledge is not.
- Birth notices are emitted only via an explicit callback hook.
- UI must display births only when epistemically known.

## Tests

`dominium_life_birth` validates:
- deterministic scheduling
- resource enforcement
- lineage determinism
- cohort/micro invariance
- epistemic gating
- batch vs step equivalence

## Prohibitions

- No fabricated persons without a causal pipeline.
- No global scans for parents or fertility.
- No omniscient birth knowledge.
