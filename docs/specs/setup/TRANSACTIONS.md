Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Setup Transactions

Transactions expand plan file intents into concrete, reversible steps.

## Stage Root
- Derived from services temp root + plan digest (`dsk_stage_<digest>`).
- All staged content is written under the stage root.

## Expansion Rules
- `copy` -> `MKDIR` (parent) + `COPY_FILE`
- `remove` -> `DELETE_FILE`
- `mkdir` -> `MKDIR`
- `dir_swap` is used when SPLAT caps support atomic swap; otherwise file-by-file.

## Journaling
- `txn_journal.tlv` is written before executing any step.
- Every step includes its inverse rollback action.

## Rollback
- Rollback executes recorded inverse steps in reverse order.
- Rollback is deterministic and never mutates live installs in place.