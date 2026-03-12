Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Integration Hooks (APRX)

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


This document enumerates the integration hooks required by the RepoX
automation and integration metadata tests.

## Required Artifacts

- Product registration via CMake (`dom_register_product`).
- Renderer backend registration via CMake (`dom_register_renderer_backend`).
- Platform backend registration via CMake (`dom_register_platform_backend`).
- CLI contracts documented in `docs/app/CLI_CONTRACTS.md`.

## Notes

- Registrations must occur during CMake configuration so the integration
  metadata report can be generated deterministically.
- Hook definitions are declarative only; no runtime behavior is implied.
