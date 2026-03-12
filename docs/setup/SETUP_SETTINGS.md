Status: CANONICAL
Last Reviewed: 2026-02-10
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Setup Settings

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Setup settings govern install mutation, trust, and rollback behavior.

## NOW (implemented)

- `install_roots`
- `package_store_path`
- `offline_cache_path`
- `trust_policy`
- `auto_repair_policy`
- `rollback_depth`
- `default_profile`

## SOON (scaffolded)

- guided install wizard policies
- disk planning heuristics

## LATER (deferred)

- background updates
- delta patch tuning

## Canonical Commands

- `setup.settings.get`
- `setup.settings.set`

Setup is the only install mutator.
