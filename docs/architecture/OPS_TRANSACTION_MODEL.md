# Ops Transaction Model (OPS0)

Status: binding.
Scope: transactional safety for all operational actions.

## Transaction states

Every ops action is a transaction with explicit state transitions:

- PLAN
- STAGE
- COMMIT
- ROLLBACK
- ABORT

## Covered actions

- install pack
- remove pack
- update pack
- change profile
- migrate instance
- repair instance
- rollback update
- create/clone/fork instance
- switch active instance

## Requirements

- No partial state allowed.
- All ops actions emit an ops log entry.
- Rollback restores the previous state exactly.
- Failures emit refusal semantics with structured payloads.

## Ops log

Ops log entries are written as append-only records under:

- `DATA_ROOT/ops/ops.log` for instance-scoped operations
- `INSTALL_ROOT/ops/ops.log` for install-scoped operations

Each entry MUST include:

- transaction_id
- action
- state
- timestamp
- result (ok | refused | failed)
- refusal (optional structured payload)

## Refusal behavior

Operations that would violate sandbox policy, integrity constraints, or
capability baselines MUST refuse with canonical refusal codes.

## See also

- `docs/architecture/REFUSAL_SEMANTICS.md`
- `docs/architecture/SANDBOX_MODEL.md`
- `docs/architecture/UPDATE_MODEL.md`
