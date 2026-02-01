Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Setup Transaction Model (OPS0-SETUP)

Status: binding.
Scope: transactional install/repair/uninstall/rollback for setup.

This model is a specialization of OPS0 for setup operations.
All setup actions are transactions with explicit stages and logs.

## Stages (authoritative)

- PLAN
- STAGE
- COMMIT
- ROLLBACK

## Rules (binding)

- No COMMIT without successful STAGE.
- Any failure triggers ROLLBACK.
- ROLLBACK restores the previous state exactly.
- All stages are logged deterministically.

## Logging

Setup writes structured ops logs under:
- `INSTALL_ROOT/ops/ops.log` for install-scoped actions.
- `DATA_ROOT/ops/ops.log` for data-root scoped actions (if install root is removed).

Each entry includes:
- transaction_id
- action
- state (PLAN | STAGE | COMMIT | ROLLBACK)
- timestamp
- result (ok | refused | failed)
- refusal (optional structured payload)

## See also

- `docs/architecture/OPS_TRANSACTION_MODEL.md`
- `docs/architecture/REFUSAL_SEMANTICS.md`
- `docs/architecture/PRODUCT_SHELL_CONTRACT.md`