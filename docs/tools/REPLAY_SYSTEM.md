Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# REPLAY SYSTEM

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.






Replays MUST be deterministic event histories sufficient to reconstruct state.


Replays MUST be distinct from saves; saves are state snapshots.


Replay tooling MUST support load, step, pause/resume, and diff operations.


Replays MUST reference packs by ID, never by path.


Replay tooling MUST be read-only and headless-safe.





References:


- docs/architecture/INVARIANTS.md


- docs/architecture/REALITY_LAYER.md
