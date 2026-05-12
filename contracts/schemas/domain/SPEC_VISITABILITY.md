# SPEC VISITABILITY (DOMAIN4)

Status: draft.
Version: 1.0
Scope: visitability gates tying reachability to refinement contracts.

## Definition: Visitable
A location is VISITABLE if:
- it is REACHABLE (see `SPEC_REACHABILITY.md`), AND
- its existence_state is REFINABLE or REALIZED, AND
- a valid refinement contract exists, AND
- refusal conditions are not met.

## Non-Visitable States
Locations in these states are not visitable by normal travel:
- DECLARED
- LATENT
- ARCHIVED
- FROZEN

Admin-only overrides require explicit effects and audit logs.

## Visitability Pipeline
1) Travel Feasibility Check (TRAVEL path + schedule)
2) Domain Permission Check (DOMAIN volumes + forbidden zones)
3) Existence State Check (EXIST0)
4) Refinement Contract Check (EXIST1)
5) Budget Gate (EXEC/HWCAPS)
6) Outcome (ACCEPT / DEFER / REFUSE)

## Outcomes
- VISIT_ACCEPT
- VISIT_DEFER (with next_due_tick and optional degradation tier)
- VISIT_REFUSE (with refusal_code)

## Refusal Codes (canonical)
- VISIT_UNREACHABLE
- VISIT_DOMAIN_FORBIDDEN
- VISIT_LAW_FORBIDDEN
- VISIT_EXISTENCE_INVALID
- VISIT_NO_CONTRACT
- VISIT_ARCHIVAL_BLOCKED
- VISIT_BUDGET_INSUFFICIENT

## Determinism Rules
- No visit without refinement or realization.
- Uncertainty yields refusal or deferral (never optimistic acceptance).
- Degradation is explicit and auditable.

## Integration Points
- EXIST0-2: existence/archival states.
- EXIST1: refinement and collapse contracts.
- DOMAIN*: domain volumes and permission checks.
- TRAVEL*: reachability proofs and scheduling.
- EXEC/HWCAPS: budget gating and deterministic deferral.

## Prohibitions
- No travel into non-visitable targets.
- No placeholder or fabricated micro environments.
- No bypass of refinement contracts.
