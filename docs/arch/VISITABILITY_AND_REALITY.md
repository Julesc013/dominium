# Visitability and Reality (DOMAIN4)

Status: draft.
Scope: binding reachability, refinement, and existence so visitable space is real.

## Core Promise
If a location can be reached, it is real, consistent, and refinable.
If it cannot be refined, it must be unreachable.

## Definitions
Reachable:
- A valid travel path exists.
- All traversed domains permit entry.
- Law and capability checks pass.
- Time/capacity can be scheduled.

Visitable:
- Reachable, AND
- existence_state is REFINABLE or REALIZED, AND
- a refinement contract exists, AND
- refusal conditions are not met.

## Visitability Pipeline
1) Travel feasibility (TRAVEL graph + schedule)
2) Domain permission (DOMAIN volumes)
3) Existence state (EXIST0)
4) Refinement contract (EXIST1)
5) Budget gate (EXEC/HWCAPS)
6) Outcome (accept, defer, refuse)

## Budget and Degradation
Budget pressure can:
- defer a visit deterministically
- degrade refinement fidelity (meso vs micro)
Budget pressure must not:
- allow visits without refinement
- fabricate placeholder environments

## Admin Overrides
Admin capability may bypass visit checks, but:
- must emit explicit effects
- must log audit records
- must respect archival rules (fork before mutation)

## Why Fake Worlds Cannot Exist
- Declared/latent targets are unreachable by normal travel.
- Refinement contracts are mandatory for visitability.
- Archived/frozen states block entry unless forked.
- Uncertainty yields refusal or deferral, not optimistic acceptance.

## References
- `schema/domain/SPEC_REACHABILITY.md`
- `schema/domain/SPEC_VISITABILITY.md`
- `docs/arch/EXISTENCE_AND_REALITY.md`
