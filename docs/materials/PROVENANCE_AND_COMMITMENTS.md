Status: CANONICAL
Last Reviewed: 2026-02-26
Supersedes: none
Superseded By: none
Version: 1.0.0
Scope: MAT-0 provenance and commitment framework
Binding Sources: docs/canon/constitution_v1.md, docs/canon/glossary_v1.md

# Provenance and Commitments

This document defines the canonical event-sourcing and commitment contract for the materials domain family.

## A) Event Sourcing Contract

- Every material-changing process must emit deterministic provenance events.
- Each event records, at minimum:
  - `event_id`
  - `process_id`
  - `input_batch_refs`
  - `output_batch_refs`
  - ledger deltas
  - tick index
- Event ordering is deterministic and replayable.

## B) Commitment Lifecycle

Canonical commitment states:

- `planned`
- `scheduled`
- `executing`
- `completed`
- `failed`

Rules:

- Commitment state changes are process-driven.
- Commitment transitions emit provenance events.
- Commitment records and event links are deterministic artifacts.

## C) Reenactment Contract

Given:

- event log,
- batch lineage,
- assembly graph,

the engine must support deterministic reconstruction of:

- meso-level reenactment,
- optional micro-level reenactment in bounded ROI.

Reenactment is derived output and does not mutate canonical truth.

## D) Compaction Contract

Compaction may summarize old event ranges, but must preserve:

- batch lineage integrity,
- invariant continuity,
- hash-chain continuity for retained canonical artifacts.

Compaction is deterministic and must preserve replayability from kept checkpoints.

