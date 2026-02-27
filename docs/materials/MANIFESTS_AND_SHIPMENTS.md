Status: DERIVED
Last Reviewed: 2026-02-27
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md`.

# Manifests And Shipments

## Purpose
Define MAT-4 manifest, shipment commitment lifecycle, and provenance obligations for deterministic logistics execution.

## Manifest Definition
A `Manifest` is a scheduled transfer contract:
- `batch_id` + `material_id` + `quantity_mass`
- source node and destination node
- deterministic depart/arrival ticks
- lifecycle status
- canonical deterministic fingerprint

## Shipment Commitments
- Every manifest must have a canonical shipment commitment.
- Commitments are authoritative artifacts (`planned`, `scheduled`, `executing`, `completed`, `failed`).
- Macro stock mutation requires a commitment-linked process event.

## Nothing Teleports
- Material transfer outside ROI must originate from:
  - `process.manifest_create`
  - `process.manifest_tick`
  - commitment/provenance events emitted by those processes
- No direct node stock edits are allowed without manifest/process lineage.

## Failure/Loss Handling
- Loss is deterministic and edge-policy driven (`loss_fraction`).
- Loss outcomes emit explicit provenance events and exception-ledger accounting.
- Failure statuses remain traceable and replayable.

## Provenance Contract
Manifest lifecycle events are canonical:
- `shipment_depart`
- `shipment_arrive`
- `shipment_lost`

Each event links:
- manifest id
- commitment id
- route metadata
- tick + actor + quantity deltas

## Reenactment Readiness
- Manifests store replay descriptors (route edges, tick windows, actor, quantities).
- Later MAT-8 reenactment can refine into micro transport without altering macro truth history.

## Constitutional Alignment
- A1 Determinism: status transitions and loss math are tick/order deterministic.
- A2 Process-only mutation: manifests and commitments gate authoritative stock edits.
- A6 Provenance continuity: shipment events remain traceable across compaction.
