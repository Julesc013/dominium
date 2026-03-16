Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# MACHINE_PORTS Baseline (ACT-4)

## Scope

ACT-4 introduces deterministic machine ports and batch interactions without inventory/crafting systems.

## Added Contracts

- Port schemas: `port`, `port_type`, `port_connection`
- Machine schemas: `machine`, `machine_type`
- Registries:
  - `port_type_registry`
  - `machine_type_registry`
  - `port_visibility_policy_registry`
  - `machine_operation_registry`

## Runtime Integration

- New deterministic port engine: `src/machines/port_engine.py`
- New process family:
  - `process.port_insert_batch`
  - `process.port_extract_batch`
  - `process.port_connect`
  - `process.port_disconnect`
  - `process.machine_operate`
  - `process.machine_pull_from_node`
  - `process.machine_push_to_node`

## Guarantees

- Process-only mutation for ports/machines.
- Deterministic ordering and IDs for connections and output batches.
- Refusal-based behavior on capacity/material mismatches.
- Provenance events emitted for port and machine operations.
- Ledger-safe transfer semantics through explicit source/destination handling.

## Interaction/Inspection Integration

- Affordance target-kind support for `machine` and `port`.
- Inspection supports machine/port targets with deterministic snapshot payloads.
- Overlay shows procedural machine/port diagnostics without assets.

## Guardrails

RepoX invariants:

- `INV-PORTS-PROCESS-ONLY`
- `INV-MACHINE_OPERATIONS-DATA-DRIVEN`
- `INV-NO-SILENT-BATCH-CREATION`

AuditX analyzers:

- `SilentBatchCreationSmell`
- `PortTruthLeakSmell`

## Notes

- Signal payload semantics remain stubbed.
- Energy network semantics remain registry/data placeholders.
- Full recipe/crafting systems remain out-of-scope.
