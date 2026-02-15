Status: DERIVED
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `schemas/budget_policy.schema.json` v1.0.0 and `tools/xstack/sessionx/process_runtime.py`.

# Budget Policy v1

## Purpose
Define deterministic compute/fidelity admission bounds for region expansion during traversal.

## Source of Truth
- `schemas/budget_policy.schema.json`
- `build/registries/budget_policy.registry.json`
- `tools/xstack/sessionx/process_runtime.py`

## Required Fields
- `policy_id`
- `activation_policy_id`
- `max_compute_units_per_tick`
- `max_entities_micro`
- `max_regions_micro`
- `fallback_behavior` (`degrade_fidelity|refuse`)
- `logging_level`
- `tier_compute_weights` (`coarse|medium|fine`)
- `entity_compute_weight`

All policy knobs are numeric/data-only; logic is not embedded in pack payloads.

## Deterministic Compute Proxy
`compute_units_used` is derived deterministically:
- `tier_sum = sum(tier_compute_weights[tier] for each active micro region)`
- `entity_sum = sum(micro_entities_target for each active micro region)`
- `compute_units_used = tier_sum + entity_sum * entity_compute_weight`

This proxy is used for budget gating and PerformX reporting.

## Enforcement Order
1. Select candidate regions deterministically.
2. Apply provisional fidelity tiers.
3. Evaluate compute/entity limits.
4. If exceeded:
   - `degrade_fidelity`: deterministic downgrade then cap.
   - `refuse`: emit `BUDGET_EXCEEDED`.

No silent overflow and no unbounded fallback.

## Run-Meta and Perceived Visibility
Budget outcomes are emitted to:
- `UniverseState.performance_state`
- script run-meta deterministic fields
- `PerceivedModel.performance` (lab law where epistemic limits allow)

## Pack-Driven Contribution
Path:
- `packs/core/policy.budget.default_lab/`

Contribution format:
- `type: "registry_entries"`
- `entry_type: "budget_policy"`
- policy payload validated by `schemas/budget_policy.schema.json`

## Example
```json
{
  "schema_version": "1.0.0",
  "policy_id": "policy.budget.default_lab",
  "activation_policy_id": "policy.activation.default_lab",
  "max_compute_units_per_tick": 240,
  "max_entities_micro": 180,
  "max_regions_micro": 24,
  "fallback_behavior": "degrade_fidelity",
  "logging_level": 2,
  "tier_compute_weights": {
    "coarse": 2,
    "medium": 5,
    "fine": 9
  },
  "entity_compute_weight": 1
}
```

## TODO
- Add policy profile families for non-lab deployments.
- Add explicit budget refusal telemetry aggregation contract.

## Cross-References
- `docs/architecture/interest_regions.md`
- `docs/architecture/fidelity_policy.md`
- `docs/architecture/macro_capsules.md`
- `docs/contracts/refusal_contract.md`
