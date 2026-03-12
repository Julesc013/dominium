Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Validation Checker

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Status: canonical.
Scope: offline comparison and invariant checks for tool outputs.
Authority: canonical. This tool MUST fail loudly on mismatch.

## Purpose
- Compare expected vs actual tool outputs.
- Detect mismatches in refinement requests and plan summaries.
- Emit optional reports under `build/cache/assets/`.

## Rules
- Validation MUST NOT modify pack data.
- Validation MUST NOT assume engine runtime state.
- Any mismatch MUST be reported explicitly.
