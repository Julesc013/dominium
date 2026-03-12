Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Rendering Epistemics

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


## Rendering Contract
- Client rendering consumes epistemic artifacts only.
- Allowed artifact classes:
  - `ObservationArtifact`
  - `MemoryArtifact`
- Authoritative truth is excluded from normal render paths.

## Render State Classes
- `OBSERVED_NOW`
- `REMEMBERED`
- `INFERRED`
- `UNKNOWN`

## Forbidden Client States
- `hidden-but-present` entity caches.
- Receiving truth payloads for occluded or out-of-range entities.

## Required Per-Renderable Metadata
- `epistemic_status`
- `confidence`
- `provenance`
- `staleness`

## Not-Visible Reason Codes
- `NOT_OBSERVED`
- `OCCLUDED`
- `OUT_OF_RANGE`
- `FORGOTTEN`
- `WITHHELD_BY_LAW`
- `NO_SENSOR_CAPABILITY`
- `BUDGET_DROPPED`

## Operational Rules
- `UNKNOWN` means not present in client renderable state.
- Transition from `UNKNOWN` to visible state requires a lawful observation artifact.
- Tool-only truth views require entitlement, watermarking, and audit logging.
