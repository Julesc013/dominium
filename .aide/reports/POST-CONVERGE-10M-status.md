# POST-CONVERGE-10M Status

Status: DERIVED
Last Reviewed: 2026-05-16

## Result

PARTIAL

## Summary

POST-CONVERGE-10M reproduced focused `inv_repox_rules`, isolated retired-domain path policy failures, and fixed the safe stale RepoX rule path assumptions. Focused RepoX improved from 51 failures / 5 warnings to 23 failures / 5 warnings.

The remaining retired-domain failures are two MW-4 fixture failures caused by `game/domains/embodiment/__init__.py` lazily importing retired `embodiment.*` modules. They are preserved as blockers because fixing them would change product/runtime source behavior.

## Counts

| Metric | Count |
| --- | ---: |
| POST-CONVERGE-10L baseline | 51 failures / 5 warnings |
| POST-CONVERGE-10M after safe fixes | 23 failures / 5 warnings |
| Retired-domain stale rule path failures fixed | 28 |
| Retired-domain source import blockers remaining | 2 |

## Scope Guard

No root moves, file moves, deletes, renames, active path aliases, layout exception retirements, product proof, portable projection proof, package proof, release proof, or product/runtime source behavior changes were made.
