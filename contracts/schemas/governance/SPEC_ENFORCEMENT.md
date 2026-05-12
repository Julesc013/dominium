--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT time and deterministic event scheduling primitives.
GAME:
- Enforcement capacity rules and constraints.
SCHEMA:
- Enforcement record format and versioning metadata.
TOOLS:
- Future editors/inspectors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No implicit or fabricated enforcement.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_ENFORCEMENT — Enforcement Capacity (CIV2)

Status: draft  
Version: 1

## Purpose
Define deterministic enforcement capacity as a bounded resource for policy
execution.

## EnforcementCapacity schema
Required fields:
- enforcement_capacity_id
- available_enforcers (cohort count or points)
- coverage_area
- response_time (ACT-derived)
- cost model (ledger obligations)

Rules:
- Enforcement capacity is explicit and bounded.
- Capacity must be checked before enforcing policies.

## Determinism requirements
- Capacity updates are event-driven.
- No per-tick global enforcement scans.

## Integration points
- Policies: `schema/governance/SPEC_POLICY_SYSTEM.md`
- Jurisdictions: `schema/governance/SPEC_JURISDICTIONS.md`

## Prohibitions
- No fabricated enforcement capacity.
