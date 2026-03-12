Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Machine Ports Model

Status: Canonical (ACT-4 baseline)

## Purpose

Machine Ports define a universal, data-driven interface for material, energy, and signal transfer between machines, structures, and logistics nodes.

## Port Types

- `port.material_in`
- `port.material_out`
- `port.energy_in`
- `port.energy_out`
- `port.signal_in` (stub)
- `port.signal_out` (stub)

Each port type declares a payload kind (`material|energy|signal`) and direction (`in|out|bidirectional`).

## Interaction Model

Ports are exposed through ActionSurfaces and resolved through ACT-1 rules.

Supported interactions:

- `insert batch` -> `process.port_insert_batch`
- `extract batch` -> `process.port_extract_batch`
- `connect` -> `process.port_connect`
- `disconnect` -> `process.port_disconnect`

Machine execution is process-driven via `process.machine_operate` and may be triggered by ACT-3 tasks.

## Tier Mapping

- Micro (ROI): explicit port interactions and deterministic batch movement between ports.
- Meso: ports connect to logistics nodes; movement is represented as node inventory deltas and provenance events.
- Macro: no global per-item inventory; only ledger-accounted stock and batch lineage.

## Determinism Rules

- Port content ordering is deterministic by `(batch_id, material_id)`.
- Connection IDs and output batch IDs are deterministic hashes of canonical inputs.
- No hidden mutation: every change is emitted as process outcome + provenance event.

## Law/Authority/Epistemics

- Port processes are law-gated and entitlement-gated.
- Ranked/server policy may restrict connect/disconnect or machine operations.
- Inspection/readout respects epistemic policy and redaction rules.

## Process-only Mutation

Ports and machines never mutate Truth directly from UI or renderer.
State changes must occur through deterministic process execution and pass conservation checks.

## Non-goals

- No full crafting UI.
- No global per-item inventory substrate.
- No heavy physical simulation of hoses/wires/conveyors.

## Extension Points

- SIG signal transport semantics (future SIG series).
- Explicit energy network substrate (future energy series).
- Advanced manufacturing recipes and scheduling policies.
