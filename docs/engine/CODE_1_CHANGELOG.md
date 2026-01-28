# CODE-1 Changelog (Interpreter Completion)

Status: binding.
Scope: interpreter extensions and tool updates to close DATA-1 gaps.

## Gap Inventory (from `docs/content/DATA_1_OVERVIEW.md`)

- Unitless numeric values not supported.  
  Classification: NUMERIC.  
  Resolution: Added `unit.dimensionless.ratio` to UNIT_SYSTEM_POLICY and core units pack; updated DATA-1 process distributions to use unitless units.
- No pressure unit exists.  
  Classification: NUMERIC.  
  Resolution: Added `unit.pressure.pascal` to UNIT_SYSTEM_POLICY and core units pack; updated pressure interfaces in DATA-1 parts to use pressure units.
- `fab_inspect` does not compare endpoint interfaces on edges.  
  Classification: TOOLING / VALIDATION.  
  Resolution: `fab_inspect` now validates edge endpoints, compares from/to interfaces, and emits compatibility traces and refusals.
- Assembly cycles lack allow/forbid policy.  
  Classification: STRUCTURAL / VALIDATION.  
  Resolution: Introduced `extensions.cycle_policy` convention (`allow`/`forbid`) and cycle checks in `fab_validate`.
- Process families cannot encode distribution types.  
  Classification: PARAMETRIC / TOOLING.  
  Resolution: Added deterministic sampling helpers (bounded sampling, multi-outcome selection) and seed composition utilities for future distribution metadata.

## Changes

- Interpreter: added seed composition and deterministic sampling helpers.
- Interpreter: added bounded sampling and multi-outcome selection utilities (extend-only).
- Tooling: `fab_validate` now checks edge endpoint interfaces and cycle policy.
- Tooling: `fab_inspect` now reports edge compatibility traces, endpoint checks, and capacity totals.
- Data: added unitless and pressure units to canonical unit tables.
- Data: updated DATA-1 packs to use the new units where appropriate.

## Traceability

- Unit gaps: `docs/arch/UNIT_SYSTEM_POLICY.md` updates and data pack unit annotations.
- Interface compatibility gap: `tools/fab/fab_inspect.py` and new edge mismatch fixture.
- Cycle policy gap: `tools/fab/fab_validate.py` and cycle fixtures.
- Distribution gap: `game/include/dominium/fab/fab_interpreters.h` + `game/rules/fab/fab_interpreters.cpp` helpers.
