# Budget Policy (BUDGET0)

Status: binding.
Scope: deterministic admission control and bounded per-commit work.

## Purpose
Budgets are policy-layer limits. They do not change simulation semantics.
They only gate admission and scheduling at commit boundaries.

## Canonical budget taxonomy (required)
Scaling and macro-time admission MUST use the following budget categories:

- ACTIVE_DOMAIN_BUDGET
  - Meaning: maximum number of Tier-2 domains active at once.
  - Policy fields: `active_domain_budget` (if non-zero) else `max_tier2_domains`.

- REFINEMENT_BUDGET
  - Meaning: micro expansion refinement work per commit tick.
  - Policy fields: `refinement_budget_per_tick`, `refinement_cost_units`.

- COLLAPSE_BUDGET
  - Meaning: micro -> macro collapse work per commit tick.
  - Policy fields: `collapse_budget_per_tick`, `collapse_cost_units`.

- MACRO_EVENT_BUDGET
  - Meaning: macro events executed per commit tick.
  - Policy fields: `macro_event_budget_per_tick`, `macro_event_cost_units`.

- AGENT_PLANNING_BUDGET
  - Meaning: planning reconstruction or macro planning steps per commit tick.
  - Policy fields: `planning_budget_per_tick`, `planning_cost_units`.

- SNAPSHOT_BUDGET
  - Meaning: snapshot/serialization work per commit tick.
  - Policy fields: `snapshot_budget_per_tick`, `snapshot_cost_units`.

Budgets are deterministic counters scoped to a commit tick. They reset only
when `now_tick` advances at a new commit boundary.

## Admission control (hard gates)
Before any operation that increases active simulation cost, the system MUST:

1) Check budget availability deterministically.
2) If insufficient, REFUSE or DEFER explicitly.
3) Emit an auditable event that includes budget context.
4) Leave authoritative state unchanged on refusal or defer.

Required admission checks include:

- domain expansion and Tier-2 activation
- macro event execution
- agent planning reconstruction
- collapse and compaction work
- snapshot/serialization work

## No implicit budget stealing
Budget exhaustion MUST NOT:

- implicitly demote other domains
- implicitly change fidelity tiers
- implicitly steal budget from other work classes

Any reallocation must be explicit, policy-driven, and auditable.

## Deterministic deferral and backlog bounds
Deferred work MUST be:

- queued in deterministic order (domain id, operation kind, reason code)
- bounded by policy (`deferred_queue_limit` and a hard cap)
- explicit in the event log

If the deferral queue is disabled or full, the system MUST emit a refusal
instead of silently accumulating work.

## Budget outcomes and refusal codes (scaling)
Scaling admission MUST use explicit, stable refusal codes where possible:

- REFUSE_ACTIVE_DOMAIN_LIMIT
- REFUSE_REFINEMENT_BUDGET
- REFUSE_MACRO_EVENT_BUDGET
- REFUSE_AGENT_PLANNING_BUDGET
- REFUSE_SNAPSHOT_BUDGET
- REFUSE_COLLAPSE_BUDGET
- REFUSE_DEFER_QUEUE_LIMIT

Generic `REFUSE_BUDGET_EXCEEDED` remains valid for unclassified cases, but
admission points SHOULD map to a specific budget refusal when available.

Deferrals remain explicit, logged, and replayable:

- DEFER_COLLAPSE
- DEFER_EXPANSION
- DEFER_MACRO_EVENT
- DEFER_COMPACTION

## Observability requirements
Budget policy and runtime state MUST be observable:

- current usage vs limits per budget category
- deferred work count and overflow
- refusal counts by budget class
- budget context attached to scaling events

## See also
- `docs/architecture/CONSTANT_COST_GUARANTEE.md`
- `docs/architecture/REFUSAL_SEMANTICS.md`
- `docs/architecture/SCALING_MODEL.md`
- `docs/architecture/ARCH0_CONSTITUTION.md`
