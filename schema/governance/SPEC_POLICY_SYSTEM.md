--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- ACT time and deterministic event scheduling primitives.
GAME:
- Policy rules, schedules, and enforcement hooks.
SCHEMA:
- Policy record format and versioning metadata.
TOOLS:
- Future editors/inspectors only (no runtime behavior).
FORBIDDEN:
- No runtime logic in schema specs.
- No policy execution without prerequisites.
DEPENDENCIES:
- Engine -> (no dependencies outside engine/).
- Game -> engine public API only.
- Schema -> none (formats only).
- Tools -> schema + engine/game public APIs only.
--------------------------------
# SPEC_POLICY_SYSTEM — Policy Model (CIV2)

Status: draft  
Version: 1

## Purpose
Define deterministic policy records that schedule governance actions.

## Policy schema
Required fields:
- policy_id
- type (taxation hook, curfew, property enforcement, election schedule)
- schedule (ACT time or T4 recurrence)
- prerequisites:
  - legitimacy threshold
  - enforcement capacity threshold
- effects (hooks into E4/INFO/CMD)
- fallback behavior on failure

Rules:
- Policies are event-driven; next_due_tick is derived from schedule.
- Policies must be deterministic and batch-vs-step equivalent.

## Determinism requirements
- Stable ordering of policy events by policy_id.
- No per-tick policy scans.

## Integration points
- Jurisdictions: `schema/governance/SPEC_JURISDICTIONS.md`
- Legitimacy: `schema/governance/SPEC_LEGITIMACY.md`
- Enforcement: `schema/governance/SPEC_ENFORCEMENT.md`
- Standards: `schema/governance/SPEC_STANDARD_RESOLUTION_GOV.md`

## Prohibitions
- No policy execution without legitimacy/capacity checks.
- No UI-driven policy changes.
