Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# FEATURE_EPOCH_POLICY (FINAL0)

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Status: draft  
Version: 1

## Purpose
Define how semantic changes are introduced without breaking determinism.

## Epoch definition
A feature epoch is a monotonic integer that gates simulation semantics.
Each epoch is owned by a subsystem and must be recorded in saves/replays.

## Epoch bump rules
- Any sim-affecting change requires an explicit epoch bump.
- Epoch bumps must include:
  - rationale
  - affected data and rules
  - migration or refusal strategy

## Migration requirements
- Schema changes that alter semantics must align with epoch bumps.
- Replays and saves must record epoch values for deterministic playback.

## Prohibitions
- Changing simulation semantics without an epoch bump.
- Retroactive reinterpretation of older epochs.
