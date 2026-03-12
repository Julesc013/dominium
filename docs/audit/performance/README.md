Status: DERIVED
Last Reviewed: 2026-02-11
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# PerformX Audit Artifacts

This directory stores deterministic performance artifacts.

## Artifact Classes

- `PERFORMX_RESULTS.json`: canonical normalized envelope results.
- `PERFORMX_REGRESSIONS.json`: canonical regression findings.
- `PERFORMX_BASELINE.json`: canonical explicit baseline.
- `RUN_META.json`: run metadata (non-canonical).

## Determinism Notes

- Canonical artifacts exclude timestamps and host identifiers.
- `RUN_META.json` may vary and is not used for determinism checks.
- Regression detection compares canonical normalized values and tolerances.
