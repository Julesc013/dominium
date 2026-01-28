# Interest System Work IR Guide (ADOPT3)

Scope: authoritative interest system Work IR emission and gating.

## Invariants
- Interest work is authoritative and emitted as Work IR only.
- Ordering and merges are deterministic.
- Pinned interest cannot be dropped by budgets.

## Dependencies
- `docs/guides/WORK_IR_EMISSION_GUIDE.md`
- `docs/architecture/EXECUTION_MODEL.md`
- `docs/architecture/REALITY_LAYER.md`

This guide defines the authoritative InterestSystem Work IR contract and how to
emit interest-related tasks deterministically.

## Scope

- Authoritative system (STRICT determinism class).
- IR-only migration state.
- Emits Work IR tasks for interest collection, merge, hysteresis, and fidelity requests.

## Source Taxonomy

Sources are declared explicitly and mapped to stable reasons:

- PLAYER_FOCUS → `DOM_INTEREST_REASON_PLAYER_FOCUS`
- COMMAND_INTENT → `DOM_INTEREST_REASON_COMMAND_INTENT`
- LOGISTICS → `DOM_INTEREST_REASON_LOGISTICS_ROUTE`
- SENSOR_COMMS → `DOM_INTEREST_REASON_SENSOR_COMMS`
- HAZARD_CONFLICT → `DOM_INTEREST_REASON_HAZARD_CONFLICT`
- GOVERNANCE_SCOPE → `DOM_INTEREST_REASON_GOVERNANCE_SCOPE`

Each source provides a deterministic `dom_interest_source_list` with stable ordering.

## Task Breakdown

The InterestSystem emits tasks in phases:

1) `DOM_INTEREST_TASK_COLLECT_SOURCES` (phase 0)
   - Reads: source feed set
   - Writes: scratch InterestSet

2) `DOM_INTEREST_TASK_MERGE` (phase 1)
   - Reads: scratch InterestSet
   - Writes: merged InterestSet

3) `DOM_INTEREST_TASK_APPLY_HYSTERESIS` (phase 2)
   - Reads: merged InterestSet
   - Reads/Writes: relevance states
   - Writes: transitions

4) `DOM_INTEREST_TASK_BUILD_REQUESTS` (phase 3)
   - Reads: transitions
   - Writes: fidelity requests

Each task declares AccessSets and has deterministic task IDs and commit keys.

## Hysteresis Rules

- Enter thresholds are higher than exit thresholds.
- `min_dwell_act` (legacy field name: `min_dwell_ticks`, deprecated terminology) prevents thrash under oscillating signals.
- Pinned entities (player focus) must never be dropped by budget degradation.

## Budgeting & Degradation

- Work is sliced deterministically via `start_index`/`count`.
- Sources are processed in fixed priority order.
- Lower tiers increase cadence and reduce per-ACT budget.
- When budget is exhausted, lower-priority sources are deferred.

## Law & Capability Gating

- Law may disable specific source kinds.
- Disallowed sources are skipped; no tasks are emitted for them.
- Interest system never bypasses law decisions.

## Forbidden assumptions

- Global scans of world objects for interest.
- Camera/render distance as primary activation trigger.
- Unordered merges without normalization.
- Direct execution outside Work IR.

## See also
- `docs/guides/DOMAIN_QUERY_AND_BUDGETS.md`
