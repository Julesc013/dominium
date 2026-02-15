Status: DERIVED
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `schemas/activation_policy.schema.json` v1.0.0, `schemas/budget_policy.schema.json` v1.0.0, and `tools/xstack/sessionx/process_runtime.py`.

# Interest Regions v1

## Purpose
Define deterministic interest-region selection for macro/micro transition control during continuous traversal.

## Source of Truth
- `schemas/activation_policy.schema.json`
- `schemas/budget_policy.schema.json`
- `schemas/fidelity_policy.schema.json`
- `tools/xstack/sessionx/process_runtime.py` (`process.region_management_tick`)
- Canon binding: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`

## TruthModel Structure
`UniverseState` fields used by region management:
- `interest_regions[]`:
  - `region_id`
  - `anchor_object_id`
  - `active`
  - `current_fidelity_tier` (`coarse|medium|fine`)
  - `last_transition_tick`
- `macro_capsules[]`
- `micro_regions[]`
- `performance_state`

## Deterministic Selection Inputs
- Camera state from `camera.main`
- Astronomy object index from compiled `astronomy.catalog.index.json`
- Activation/Budget/Fidelity policies from compiled policy registries
- Current simulation tick

No wall-clock, no nondeterministic IO ordering, no background-thread authority decisions.

## Selection Algorithm (v1)
1. Build candidate objects from compiled astronomy entries only.
2. Compute deterministic distance proxy from camera position (`camera_manhattan_mm`).
3. Apply activation rule by object kind (`interest_radius_rules` with `*` fallback).
4. Sort candidates by `(priority, object_id)` stable order.
5. Select up to `max_regions_micro`.
6. Select fidelity tier via deterministic policy thresholds + hysteresis.
7. Enforce compute/entity budgets:
   - degrade fidelity by deterministic `degrade_order`
   - then cap active set if still over budget
   - or refuse when policy fallback is `refuse`.

## Transition Ordering Invariant
Transition application order is deterministic and explicit:
1. `collapse` transitions first (stable `region_id` order)
2. `expand` transitions second (stable `region_id` order)

This ordering is stable across replay and worker-count variations.

## Refusal and Degrade Behavior
- Refuse on missing policy/registry inputs:
  - `REGISTRY_MISSING`
  - `PROCESS_INPUT_INVALID`
- Budget hard refusal when fallback policy is `refuse`:
  - `BUDGET_EXCEEDED`
- Conservation breach refusal:
  - `CONSERVATION_VIOLATION`

When fallback is `degrade_fidelity`, the system degrades/caps deterministically instead of melting down.

## Mod Extension (Pack-Only)
To add or replace interest behavior:
1. Add policy pack under `packs/core/policy.activation.*`.
2. Contribute `registry_entries` payload with `entry_type: "activation_policy"`.
3. Add corresponding budget/fidelity policy rows as needed.
4. Include policy pack in a bundle and regenerate lockfile/registries.

No runtime code branching is permitted for per-pack policy behavior.

## Example
```json
{
  "region_id": "region.object.earth",
  "anchor_object_id": "object.earth",
  "active": true,
  "current_fidelity_tier": "fine",
  "last_transition_tick": 42
}
```

## TODO
- Add deterministic screen-space proxy option when fully derived from canonical camera/perceived inputs.
- Add explicit domain-specific priority weighting guidance for non-astronomy domains.

## Cross-References
- `docs/architecture/macro_capsules.md`
- `docs/architecture/budget_policy.md`
- `docs/architecture/fidelity_policy.md`
- `docs/architecture/camera_and_navigation.md`
- `docs/contracts/refusal_contract.md`
