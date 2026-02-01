Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# MMO Ops Acceptance (MMO-2)

This roadmap slice anchors operational survivability work.

## Acceptance Anchors

- `MMO2-CHECKPOINT-001`: deterministic, commit-boundary checkpoints.
- `MMO2-RECOVERY-002`: crash recovery from checkpoint + log tail.
- `MMO2-LIFECYCLE-003`: explicit shard lifecycle transitions.
- `MMO2-ROLLING-004`: mixed-version safety via capability overlap.
- `MMO2-OPS-005`: partial inputs refuse explicitly without corruption.
- `MMO2-LOG-006`: cross-shard log positions are checkpointed.

## Definition of Done (Ops)

- Checkpoints are policy-driven and observable.
- Recovery is deterministic and crash-only.
- Rolling updates use checkpoint -> restart -> resync.
- Lifecycle state and refusal rates are inspectable.