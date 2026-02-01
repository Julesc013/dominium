Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Constant-Cost Guarantee (SCALE3)





Status: binding.


Scope: bounded per-commit simulation cost under scaling and macro time.





## Guarantee





For a fixed set of active Tier-2 domains, per-commit simulation cost is


bounded independently of:





- total world size


- total population


- simulation history length


- number of collapsed domains





This is enforced by deterministic budgets and admission control, not by


changing simulation semantics.





## Required mechanisms





The constant-cost guarantee depends on the following binding requirements:





- all admission points that increase active work MUST be budget-gated


- deferred work MUST be bounded by policy and a hard cap


- macro-time execution MUST be event-driven or coarse-stepped only


- scheduling and deferral order MUST be deterministic


- no implicit tier changes or hidden work are allowed





## Policy surface (canonical budgets)





At minimum, the following budgets MUST exist and be enforced:





- ACTIVE_DOMAIN_BUDGET


- REFINEMENT_BUDGET


- COLLAPSE_BUDGET


- MACRO_EVENT_BUDGET


- AGENT_PLANNING_BUDGET


- SNAPSHOT_BUDGET





Each budget class MUST have:





- a deterministic policy limit


- a deterministic cost unit


- explicit refusal or deferral behavior


- observable usage and refusal counts





## Failure modes are explicit





Budget pressure MUST surface as explicit refusals or explicit deferrals:





- refusals and deferrals MUST be logged


- refusals and deferrals MUST be replayable


- refusals and deferrals MUST NOT mutate authoritative state





Silent degradation or hidden throttling violates this guarantee.





## Notes





This guarantee does not promise zero backlog. It promises that backlog and


active work remain bounded, explicit, and policy-controlled.





## Related invariants





- SCALE0-DETERMINISM-004


- SCALE3-BUDGET-009


- SCALE3-ADMISSION-010


- SCALE3-CONSTCOST-011





## See also





- `docs/architecture/BUDGET_POLICY.md`


- `docs/architecture/SCALING_MODEL.md`


- `docs/architecture/MACRO_TIME_MODEL.md`
