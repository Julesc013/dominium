Status: DERIVED
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# DIAG0 Retro Audit

## Existing Surfaces

- APPSHELL-2 already provides `diag snapshot` via `src/appshell/diag/diag_snapshot.py`.
- APPSHELL-6 supervisor crash handling still emitted snapshot bundles rather than
  full repro bundles.
- SERVER-MVP-0 server console exposed `emit_diag` but only wrote a stub JSON.
- Structured logs, proof anchors, IPC attach records, pack locks, and contract
  hashes are already locally available without network access.

## Gaps Before DIAG-0

- no canonical repro bundle schema family
- no deterministic bundle hash over ordered bundle contents
- no replay verifier for bundle integrity
- no offline capture path that consolidated run manifest, pack compatibility
  hashes, proof anchors, canonical events, and log windows

## Integration Points Chosen

- keep `diag snapshot` unchanged for APPSHELL-2 compatibility
- add `diag capture` as the DIAG-0 canonical bundle command
- reuse AppShell log ring buffers and IPC attach records
- upgrade supervisor crash capture and server `emit_diag` to the DIAG-0 builder
