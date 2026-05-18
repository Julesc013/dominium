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

## Still Blocking Later Work

- DOE-00 remains blocked.
- Feature work remains blocked.
- MOVE-BULK B-G remains unauthorized until refined and gated.
- Full CTest remains blocked by semantic lint lanes outside NAME-00.
