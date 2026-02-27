Status: DERIVED
Last Reviewed: 2026-02-27
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md`.

# Provenance And Commitments

## Purpose
Define deterministic event-sourced provenance and canonical commitment lifecycle rules for material-changing processes.

## A) Event Sourcing Contract
Every material-changing process emits an authoritative event artifact.

Minimum event payload:
- `event_id`
- `process_id`
- `tick`
- input batch references
- output batch references
- ledger deltas

Constitutional requirements:
- event payload ordering is deterministic
- ledger deltas are fixed-point and replay-safe
- each event is linked into an auditable hash chain
- events are replayable without wall-clock input

## B) Commitment Lifecycle Contract
Commitment states:
1. `planned`
2. `scheduled`
3. `executing`
4. `completed`
5. `failed`

Lifecycle requirements:
- state transitions are process-mediated and deterministic
- each transition emits an event artifact
- failed commitments preserve forensic context (`reason_code`, affected batches, affected AG nodes)
- commitment state changes must be legal under active LawProfile and AuthorityContext

## C) Reenactment Contract
Given:
- event log
- batch lineage
- assembly graph

The engine must reconstruct:
- meso-level reenactment (required)
- micro-level reenactment in ROI (optional, policy/lens gated)

Reenactment constraints:
- deterministic ordering and deterministic reductions
- no hidden mutation paths outside replayed events
- reenactment output hash stability under equivalent inputs

## D) Compaction Contract
Compaction may summarize old event ranges into deterministic checkpoints.

Compaction must preserve:
- batch lineage integrity
- invariant continuity
- event/hash-chain continuity

Allowed:
- checkpointed summary state for pre-checkpoint history

Forbidden:
- lineage-breaking compression
- semantic rewrites of causal history
- silent drop of required audit links

## Authority and Refusal Rules
- Material state mutation without event emission is refused.
- Macro changes without an antecedent commitment (or lawful exception-ledger entry) are refused.
- Reenactment requests outside epistemic scope must return deterministic refusal.

## Constitutional Alignment
- A1 Determinism is primary.
- A2 Process-only mutation.
- A3 Law-gated authority.
- A6 Provenance is mandatory.
- E6 Replay equivalence.
- E7 Hash-partition equivalence.
