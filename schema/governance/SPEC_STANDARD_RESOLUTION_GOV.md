--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Core standard resolution primitives (T4/E2/STD).
GAME:
- Governance policy binding for standards resolution.
SCHEMA:
- Standard resolution governance policies and versioning metadata.
TOOLS:
- Future editors/inspectors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_STANDARD_RESOLUTION_GOV — Governance Standard Resolution (CIV2)

Status: draft  
Version: 1

## Purpose
Define governance-standard resolution order consistent with T4/E2.

## Resolution order
Standards are resolved deterministically in this order:
1) explicit contract/policy context
2) organization standard
3) jurisdiction default
4) personal preference
5) fallback canonical numeric forms

## Determinism requirements
- Resolution order is stable and deterministic.
- Conflicts are visible epistemically (no silent override).

## Integration points
- Time standards: `docs/SPEC_TIME_STANDARDS.md`
- Money standards: `docs/SPEC_MONEY_STANDARDS.md`
- Numeric standards: `docs/SPEC_NUMERIC.md`

## Prohibitions
- No UI-driven standard override outside of explicit context.
