Status: DERIVED
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `schemas/universe_state.schema.json` v1.0.0 and `tools/xstack/sessionx/process_runtime.py`.

# Macro Capsules v1

## Purpose
Define the deterministic collapsed representation for regions not currently expanded to micro simulation.

## Contract
Each capsule row (`UniverseState.macro_capsules[]`) includes:
- `capsule_id`
- `covers_object_id`
- `conserved_quantities`
  - `mass_stub` (required scalar conserved metric in v1)
  - `entity_count`
- `fidelity_representation`
  - `tier` (`macro|expanded`)
  - `summary`
- `collapsed_micro_state_hash`

## Expand/Collapse Interface
v1 uses single deterministic process:
- `process.region_management_tick`

Transition intent is derived from policy + camera + index data; no ad hoc mutation path exists.

## Conservation Invariant
For every transition tick:
- `sum(macro_capsules.mass_stub) + sum(micro_regions.mass_stub)` must remain invariant.
- Violations refuse with `CONSERVATION_VIOLATION`.

This is intentionally minimal and forward-extensible to richer conserved quantities.

## Deterministic Transition Rules
- Collapse before expand.
- Stable ordering by `region_id`.
- Stable micro entity targets from fidelity policy tiers.
- Capsule hash anchors use canonical serialization.

## No Direct Mutation Rule
- UI/tools never mutate capsules directly.
- Mutations happen only through process execution.
- Renderer and observation remain read-only with respect to TruthModel capsules.

## Example
```json
{
  "capsule_id": "capsule.object.earth",
  "covers_object_id": "object.earth",
  "conserved_quantities": {
    "mass_stub": 31337,
    "entity_count": 0
  },
  "fidelity_representation": {
    "tier": "macro",
    "summary": "collapsed"
  },
  "collapsed_micro_state_hash": "7f57de5eaa3f5af608bbf15dd6f90f84db264f7f1f923f0a7f4f3db84fc4f892"
}
```

## TODO
- Add explicit per-domain conserved quantity maps once domain process packs are introduced.
- Add macro event hooks for collapsed regions.

## Cross-References
- `docs/architecture/interest_regions.md`
- `docs/architecture/fidelity_policy.md`
- `docs/contracts/refusal_contract.md`
