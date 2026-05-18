# NAME-00 Blockers

Status: `NO_IMMEDIATE_NAME_00_BLOCKERS`

## Immediate Blockers

None.

## Transitional Debt

The following are not blockers for NAME-00 because this task is no-apply and the debt is either historical, generated-adjacent, or already excepted:

- historical `src`, `source`, `legacy`, `common`, and `shared` path terms under `archive/`;
- `packs/source/**` content identity debt under an active bad-root exception;
- active `compat/`, `core/`, `control/`, `data/`, `lib/`, `libs/`, `meta/`, `net/`, `validation/`, and other former bad roots;
- planned internal rename targets such as `runtime/appshell`, `game/domains`, `content/domain-data`, and `contracts/schemas`;
- Python in active engine/game/runtime surfaces and former bad roots.

Current redo counts:

- no `src`/`source`/`sources` directory findings: 106 total, 13 warnings, 0 blockers.
- forbidden path-term findings: 1,450 total, 78 warnings, 0 blockers.
- directory naming findings: 418 total, 39 warnings, 0 blockers.
- file naming findings: 5,361 total, 4,307 warnings, 0 blockers.
- language ownership finding classes: 4 warnings, 0 blockers.
- current MOVE-SCRIPT-00 bad-root inventory: 1,765 tracked files, 1,593 route candidates, 172 skipped/deferred, 0 target collisions.

## Still Blocking Later Work

- DOE-00 remains blocked.
- Feature work remains blocked.
- MOVE-BULK B-G remains unauthorized until refined and gated.
- Full CTest remains governed by TEST-PERF-01 sharding.
- MOVE-BULK B-G apply remains blocked until `MOVE-BULK-BG-REFINEMENT-00` turns the dry-run router evidence into smaller approved subsets.
