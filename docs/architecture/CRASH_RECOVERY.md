Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Crash Recovery (MMO-2)

Crash recovery follows a crash-only design:
authoritative state is reconstructed strictly from persisted data.

## Recovery Procedure (Authoritative)

On shard restart:

1) Load the last committed checkpoint.
2) Load the cross-shard log tail beginning at the checkpoint position.
3) Reapply events deterministically.
4) Resume simulation.

No best-effort reconstruction is allowed.
If required data is missing, the system MUST refuse authoritatively.

## Refusal Conditions

Recovery MUST refuse explicitly when:

- no committed checkpoint exists,
- the log tail is missing or truncated,
- capability baselines or schema versions are incompatible,
- required shard snapshots are missing.

Refusals MUST:

- be explicit,
- be logged,
- be replayable.

Frozen or inspect-only modes are valid fallbacks when authority
cannot be re-established.

## Determinism Notes

Recovery MUST NOT depend on wall-clock time.
Recovery ordering MUST be stable across thread counts and platforms.

## Invariants (Test Anchors)

- `MMO2-RECOVERY-002`: Recovery from checkpoint + log tail yields the
  same authoritative state as uninterrupted simulation.
- `MMO2-OPS-005`: Partial or incompatible recovery inputs refuse
  explicitly without corrupting state.