# SPEC REACHABILITY (DOMAIN4)

Status: draft.
Version: 1.0
Scope: deterministic reachability gates for travel and interaction.

## Definition: Reachable
A location is REACHABLE if all of the following hold:
- A valid travel path exists (TRAVEL graph or equivalent).
- Every traversed domain volume permits entry.
- Law/capability gates permit travel for the actor.
- Required time and capacity can be scheduled.

Reachability is independent of refinement fidelity.

## Required Inputs
The reachability decision is a pure function of:
- travel_path_id (or path proof)
- domain_id sequence (ordered)
- law_context hash (capabilities, jurisdiction list)
- scheduling constraints (time, capacity, windows)
- actor_id (for law and capability)

## Determinism Rules
- No wall-clock or runtime benchmarking.
- Ordered, stable path evaluation.
- Domain checks must use DOMAIN runtime API only.
- Uncertainty yields refusal (no optimistic reachability).

## Outcomes
- REACH_ACCEPT
- REACH_DEFER (with next_due_tick)
- REACH_REFUSE (with refusal_code)

## Refusal Codes (canonical)
- TRAVEL_NO_PATH
- DOMAIN_FORBIDS_ENTRY
- LAW_FORBIDS_TRAVEL
- CAPACITY_INSUFFICIENT
- ARCHIVAL_BLOCKED

## Integration Points
- TRAVEL*: path feasibility, transit costs, and scheduling.
- DOMAIN*: domain volume containment and entry permissions.
- LAW: jurisdiction resolution and capability checks.
- EXEC/HWCAPS: budgeted admission and deterministic deferral.

## Prohibitions
- No implicit reachability inference.
- No travel into DECLARED/LATENT-only targets.
- No bypass of domain API checks.
