# POST-CONVERGE-10M Retired-Domain Findings

Status: DERIVED
Last Reviewed: 2026-05-16

## Summary

POST-CONVERGE-10M checked 30 retired-domain path policy failures from the focused RepoX set.

## Safe Fixes

| Finding | Count | Classification | Disposition |
| --- | ---: | --- | --- |
| RepoX stale rule paths for embodiment, geology, worldgen refinement, universe, and diagnostics | 28 | `stale_current_reference` | Fixed in `scripts/ci/check_repox_rules.py`. |
| RepoX group cache did not hash direct file dependencies | 0 | `retired_domain_rule_false_positive` | Fixed so normal CTest does not reuse stale rule-output cache after rule edits. |

The canonical replacements were exact current files under `game/domain/embodiment`, `game/domain/geology`, `game/domain/worldgen/refinement`, `game/domain/universe`, and `runtime/diagnostics`.

## Blocked

| Rule | Path | Classification | Reason |
| --- | --- | --- | --- |
| `INV-REFINEMENT-BUDGETED` | `game/domain/embodiment/__init__.py` | `real_current_policy_violation` | The MW-4 stress fixture reaches a stale `embodiment.*` lazy import. Fixing it would change product/runtime source behavior. |
| `INV-NO-BLOCKING-WORLDGEN-IN-UI` | `game/domain/embodiment/__init__.py` | `real_current_policy_violation` | The MW-4 viewer stress fixture reaches the same stale lazy import. |

## Not Touched

Historical, audit, generated, root-recycling, and archive references were not rewritten. No roots were moved, no aliases were created, and no layout exceptions were retired.
