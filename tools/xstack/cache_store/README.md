Status: DERIVED
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/architecture/registry_compile.md` and `docs/architecture/lockfile.md`.

# Registry Compile Cache Store

## Purpose
Provide content-addressed reuse for deterministic registry compile outputs and lockfiles.

## Key Contract
Cache key is a Merkle hash over:
- sorted canonical pack manifests
- sorted canonical contribution descriptors
- canonical bundle selection input
- registry compile tool version

## Invariants
- Canonical artifacts must not include nondeterministic timestamps.
- Cache manifest may include run-meta timestamps only.
- Cache hit restores outputs bitwise from stored artifacts.

## Cross-References
- `tools/xstack/cache_store/store.py`
- `tools/xstack/registry_compile/compiler.py`
- `docs/canon/constitution_v1.md`
