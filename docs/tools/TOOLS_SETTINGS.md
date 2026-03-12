Status: CANONICAL
Last Reviewed: 2026-02-10
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Tools Settings

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Tool settings are local output/inspection preferences and are read-only by default.

## NOW (implemented)

- `output_format`
- `verbosity`
- `filter_options`
- `display_options`

## Rule

Tool commands that mutate state must require explicit mutation commands; settings surfaces
must remain observational by default.
