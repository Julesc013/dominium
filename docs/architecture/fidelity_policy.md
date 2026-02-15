Status: DERIVED
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `schemas/fidelity_policy.schema.json` v1.0.0 and policy registries compiled by `tools/xstack/registry_compile/compiler.py`.

# Fidelity Policy v1

## Purpose
Define deterministic tier switching for micro detail in active interest regions.

## Source of Truth
- `schemas/fidelity_policy.schema.json`
- `build/registries/fidelity_policy.registry.json`
- `tools/xstack/sessionx/process_runtime.py`

## Required Fields
- `policy_id`
- `tiers[]`:
  - `tier_id` (`coarse|medium|fine`)
  - `max_distance_mm`
  - `micro_entities_target`
- `switching_rules`:
  - `upgrade_hysteresis_mm`
  - `degrade_hysteresis_mm`
  - `degrade_order`
  - `upgrade_order`
- `minimum_tier_by_kind` (optional but explicit map when used)

No silent defaults are allowed in policy payloads.

## Deterministic Tier Rules
- Tier decision depends only on deterministic inputs:
  - camera distance proxy
  - object kind
  - prior tier
  - policy thresholds/hysteresis
- Threshold evaluation uses stable sort on `max_distance_mm`.
- Upgrade/degrade order is policy data, not code branch toggles.

## Budget Interaction
When budget is exceeded:
1. Apply fidelity downgrade in deterministic `degrade_order`.
2. Recompute compute usage.
3. Cap active set if still over budget (for degrade fallback policy).
4. Refuse only if budget policy fallback is `refuse`.

## Mod Extension Steps
1. Create pack under `packs/core/policy.fidelity.*`.
2. Add `registry_entries` contribution with `entry_type: "fidelity_policy"`.
3. Reference policy ID from SessionSpec and lock/compile flow.
4. Validate through `tools/xstack/run fast|strict`.

## Example
```json
{
  "schema_version": "1.0.0",
  "policy_id": "policy.fidelity.default_lab",
  "tiers": [
    {
      "tier_id": "fine",
      "max_distance_mm": 1200000000000,
      "micro_entities_target": 12
    },
    {
      "tier_id": "medium",
      "max_distance_mm": 6000000000000,
      "micro_entities_target": 6
    },
    {
      "tier_id": "coarse",
      "max_distance_mm": 65000000000000000,
      "micro_entities_target": 2
    }
  ],
  "switching_rules": {
    "upgrade_hysteresis_mm": 1000000000,
    "degrade_hysteresis_mm": 1000000000,
    "degrade_order": [
      "fine",
      "medium",
      "coarse"
    ],
    "upgrade_order": [
      "coarse",
      "medium",
      "fine"
    ]
  }
}
```

## TODO
- Add per-domain tier semantic guidance (physics, AI, ecology) for later prompts.

## Cross-References
- `docs/architecture/interest_regions.md`
- `docs/architecture/budget_policy.md`
- `docs/architecture/macro_capsules.md`
