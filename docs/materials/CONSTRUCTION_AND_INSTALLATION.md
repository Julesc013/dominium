Status: DERIVED
Last Reviewed: 2026-02-27
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md`.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Construction And Installation

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


## Purpose
Define deterministic MAT-5 construction and installation process contracts for commitment-driven assembly progression.

## Canonical Model
- Construction is a process family that:
  - debits material stocks from logistics node inventories
  - credits installed-part outcomes through provenance-linked batch outputs
  - emits canonical provenance events
  - creates and advances milestone commitments
- AssemblyGraph (AG) artifacts remain the canonical structural specification.
- Installed structure state is authoritative macro/meso representation and must remain derivable/replayable.

## Deterministic Staging
- Construction runs in deterministic staged steps over ticks.
- Step scheduling uses stable ordering (`project_id`, `ag_node_id`, `step_id`).
- Parallel step execution is policy-governed and deterministic.
- No micro tool interaction is required for authoritative mutation.

## Process-Only Mutation
- No macro installation state may change outside process commit boundaries.
- Authoritative mutation paths:
  - `process.construction_project_create`
  - `process.construction_project_tick`
  - `process.construction_pause`
  - `process.construction_resume`
- UI/renderer layers may inspect/preview only.

## Commitment Requirements
- Every project has milestone commitments for deterministic start/end obligations.
- Commitment IDs are canonical artifacts referenced by project and step state.
- Nothing just happens: installation requires commitments and provenance events.

## Ledger Requirements
- Material consumption and installation transformation must be reflected in conservation accounting.
- Unaccounted deltas are forbidden in strict conservation modes.
- Loss/waste requires explicit exception-ledger entries.

## Reenactment Requirements
Each installation step must be reconstructible using:
- project and step identifiers
- consumed input batches/material quantities
- output batch identifiers
- timing (scheduled and realized tick bounds)
- actor subject identifiers

This enables MAT-8 watchability/refinement without altering macro truth history.

## Constitutional Alignment
- A1 Determinism: stable scheduling and event ordering.
- A2 Process-only mutation: construction/install state changes via processes only.
- A6 Provenance continuity: step-level causal links preserved.
- A9 Pack-driven integration: policies/event types/data are registry-driven.
