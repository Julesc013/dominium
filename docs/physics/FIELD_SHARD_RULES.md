Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Field Shard Boundary Rules

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Status: CANONICAL
Last Updated: 2026-03-04
Scope: PHYS-2 shard-safe field continuity and merge contract.

## 1) Core Rule

Field systems must not query or mutate cross-shard authoritative state directly.

## 2) Boundary Exchange Mechanism

Allowed mechanism:

- shard boundary artifacts carrying field samples/edge conditions
- deterministic merge at receiving shard boundary process

Forbidden mechanism:

- direct in-process reads into neighbor shard field tables
- direct remote mutation of `field_layers`/`field_cells`

## 3) Deterministic Merge Requirements

Boundary merge must be deterministic under equivalent inputs:

- stable ordering by `(field_id, spatial_node_id, source_shard_id)`
- explicit conflict resolution policy id
- canonical fingerprint for merged rows

## 4) Proof and Replay Expectations

When boundary exchange occurs:

- include deterministic boundary artifacts in proof window
- replay must reproduce identical boundary-driven field samples

Any replay divergence is a determinism failure.

## 5) Implementation Notes (PHYS-2)

- no additional shard transport implementation is required in this phase
- this document freezes the contract for PHYS-3+ field transport generalization
