Status: DERIVED
Last Reviewed: 2026-02-27
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md`.

# Provenance Events

## Purpose
Define MAT-5 canonical provenance event contracts for construction, installation, and material transformation history.

## Canonical Event Types
- `event.construct_project_created`
- `event.construct_step_started`
- `event.construct_step_completed`
- `event.install_part`
- `event.deconstruct_part`
- `event.material_consumed`
- `event.batch_created`

Optional extension stub:
- `event.maintenance_scheduled`

## Event Sourcing Contract
- Construction and installation changes are event-sourced.
- Each event is deterministic, replayable, and causally linked.
- Event IDs and fingerprints are deterministic for identical inputs.

## Required Event Shape
Each provenance event records:
- identity: `event_id`, `event_type_id`, `deterministic_fingerprint`
- timing: `tick`
- actor: `actor_subject_id`
- location: `site_ref`
- causality: `linked_project_id`, `linked_step_id`
- lineage: `inputs` batch refs, `outputs` batch refs
- accounting: `ledger_deltas` map (`quantity_id -> delta`)

## Causal Linkage
- `construct_project_created` starts project lineage.
- `construct_step_started` links committed step start and input reservations.
- `material_consumed` links stock debits to step execution.
- `batch_created` links transformation output batches.
- `install_part` links structural installation output to AG node completion.
- `construct_step_completed` closes step lifecycle.
- `deconstruct_part` (future path) reverses installation lineage deterministically.

## Compaction And Replay
- Events may be compacted with checkpointing only if causal continuity remains verifiable.
- Reenactment must be possible at meso level from event stream + project/step lineage.

## Constitutional Alignment
- A1 Determinism: canonical event order and fingerprints.
- A2 Process-only mutation: macro changes must cite process events.
- A6 Provenance continuity: batch and project lineage remain traceable.
