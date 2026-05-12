--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT time and deterministic event scheduling primitives.
GAME:
- Legitimacy rules, thresholds, and event updates.
SCHEMA:
- Legitimacy record format and versioning metadata.
TOOLS:
- Future editors/inspectors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No random legitimacy changes.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_LEGITIMACY — Legitimacy Model (CIV2)

Status: draft  
Version: 1

## Purpose
Define legitimacy as a deterministic, event-driven resource that constrains
governance authority.

## LegitimacyState schema
Required fields:
- legitimacy_id
- legitimacy_value (fixed-point, deterministic)
- sources (tax compliance, service delivery, security, welfare)
- decay/regen rules (event-driven)
- thresholds:
  - stable
  - contested
  - failed
- next_due_tick (ACT)

Rules:
- Updates are scheduled events only (no per-tick drift).
- Legitimacy values are bounded and deterministic.

## Determinism requirements
- Event ordering is deterministic.
- Batch vs step equivalence must hold.

## Integration points
- Taxation outcomes (E4) -> legitimacy events
- CIV1 service delivery -> legitimacy events
- Policy prerequisites: `schema/governance/SPEC_POLICY_SYSTEM.md`

## Prohibitions
- No wall-clock time usage.
- No stochastic legitimacy updates.
