Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# RENDER_BACKEND_LIFECYCLE (FINAL0)

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/archive/audit/CANON_MAP.md` and `docs/archive/audit/DOC_DRIFT_MATRIX.md`.


Status: draft
Version: 1

## Purpose
Define the lifecycle of renderer backends and their deprecation rules.

CONVERGE-11 cross-reference: current renderer matrix rows and support tiers are recorded in `contracts/release/component_matrix.contract.toml` and `docs/release/RENDER_BACKEND_MATRIX.md`. Lifecycle terms in this policy must be reconciled with matrix status during CONVERGE-12 stale-doc cleanup.

## Lifecycle stages
- **Active**: supported and tested in CI.
- **Deprecated**: supported for compatibility, no new features.
- **Retired**: removed only after documented deprecation window.

## Deprecation rules
- Deprecation requires:
  - explicit notice in this document
  - replacement path
  - minimum support window
- Removal requires updating:
  - this lifecycle document
  - compatibility promises
  - CI enforcement matrix (FINAL-RENDER-001)

## Prohibitions
- Removing a backend without documenting lifecycle impact.
- Silent renderer capability changes.
