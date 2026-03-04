# CHEM Stress Degradation Policy (CHEM-4)

Status: Normative for CHEM stress envelope tooling  
Version: 1.0.0

## Scope

This policy governs deterministic budget degradation for CHEM stress execution in:

- `tools/chem/tool_run_chem_stress.py`

It does not change runtime CHEM semantics. It governs stress-envelope behavior and diagnostics only.

## Degradation Order

When budget pressure occurs, degradation MUST be applied in this fixed order:

1. `degrade.chem.tick_bucket`
2. `degrade.chem.reaction_to_c0`
3. `degrade.chem.defer_noncritical_yield`
4. `degrade.chem.eval_cap`

The harness records step order as `step_order` and emits both:

- decision log rows (`reason_code`)
- degradation event rows (`event_kind`)

## Determinism Requirements

- Events are evaluated in deterministic run order.
- Degradation events are sorted by `(tick, run_id, step_order, event_kind)` for reporting.
- Any detected ordering drift fails `degradation_order_deterministic`.

## Logging Requirements

Every degradation activation in stress runs must produce explicit artifacts:

- `extensions.decision_log_rows`
- `extensions.degradation_event_rows`

No silent downgrade is allowed in CHEM stress tooling.
