# LIFE Death Pipeline (LIFE2)

This guide describes the deterministic death pipeline and estate scheduling
implemented in LIFE2. It is a developer reference for integrating gameplay
systems without breaking determinism, ledger conservation, or epistemic rules.

## Pipeline summary

1) Validate body and person
2) Mark body dead (no deletion)
3) Create Estate (accounts re-owned by estate, balances unchanged)
4) Append DeathEvent record
5) Schedule inheritance resolution via ACT due-event scheduler
6) Emit audit log entry and optional epistemic notice

All steps are deterministic and replay-safe.

## Key modules

- `game/include/dominium/life/death_pipeline.h`
  - `life_handle_death(...)` entrypoint
- `game/include/dominium/life/estate.h`
  - estate records, account ownership, person→account mapping
- `game/include/dominium/life/inheritance_scheduler.h`
  - ACT-based scheduling with `dg_due_scheduler`
- `game/include/dominium/life/death_event.h`
  - append-only DeathEvent records
- `game/include/dominium/life/life_audit_log.h`
  - audit log of death/estate actions

## Determinism and ordering

- Account IDs are sorted before storing in an estate record.
- DeathEvent and Estate IDs are allocated monotonically.
- Inheritance scheduling uses `dg_due_scheduler` with `estate_id` as stable key.
- Batch vs step equivalence is required for inheritance actions.

## Ledger integration

- Estate creation reassigns account ownership to the estate.
- Ledger balances never change during death handling.
- Transfers occur only through scheduled ledger transactions in later phases.

## Epistemic boundary

- Death events are authoritative; knowledge is not.
- A death notice is emitted only via an explicit callback (`notice_cb`).
- UI must display death information only when epistemically known.

## Common failures and fixes

- `LIFE_DEATH_REFUSAL_BODY_NOT_ALIVE`: body not registered or already dead.
- `LIFE_DEATH_REFUSAL_LEDGER_ACCOUNT_MISSING`: account not registered or missing in ledger.
- `LIFE_DEATH_REFUSAL_ESTATE_ALREADY_EXISTS`: death reprocessed for same person.
- `LIFE_DEATH_REFUSAL_SCHEDULE_INVALID`: invalid ACT schedule or claim period.

## Tests

`dominium_life_death` validates:
- deterministic death → estate ordering
- ledger balance conservation
- ACT schedule equivalence (batch vs step)
- executor authority enforcement
- epistemic notice hook behavior
- replay equivalence hashes

## Prohibitions

- No respawn points or fabricated heirs.
- No implicit asset transfers.
- No global scans over persons or estates.
- No OS time or platform APIs in game code.
