Status: DERIVED
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `schemas/pack_manifest.schema.json` and `docs/architecture/pack_system.md`.

# Pack Loader

## Purpose
Discover and validate pack manifests under `packs/` with deterministic refusal behavior.

## Invariants
- Manifest validation is strict and schema-driven.
- Dependency resolution is deterministic and topologically ordered.
- Duplicate IDs, missing dependencies, version conflicts, and cycles refuse.
- Pack directories cannot contain executable files.

## Cross-References
- `tools/xstack/pack_loader/loader.py`
- `tools/xstack/pack_loader/dependency_resolver.py`
- `docs/canon/constitution_v1.md`
