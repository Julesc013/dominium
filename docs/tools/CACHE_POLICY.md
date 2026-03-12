Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Cache Policy

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Status: canonical.
Scope: tool-generated derived data only.
Authority: canonical. Tools and packs MUST follow this.

## Binding rules
- All derived data MUST be written under `build/cache/assets/`.
- Derived data MUST be disposable and regenerable.
- Pack directories MUST remain source-only and immutable to tools.
- Cache deletion MUST NOT affect saves or packs.
