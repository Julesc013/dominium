Status: DERIVED
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/architecture/registry_compile.md`, `docs/architecture/lockfile.md`, and Canon v1.0.0.

# Registry Compile v1

## Purpose
Compile deterministic derived registries and lockfiles from pack manifests and typed contributions.

## Inputs
- Pack manifests resolved by `tools/xstack/pack_loader/`
- Typed contributions from `tools/xstack/pack_contrib/`
- Bundle selection from `bundles/<bundle_id>/bundle.json` via `tools/xstack/registry_compile/bundle_profile.py`

## Outputs
- `domain.registry.json`
- `law.registry.json`
- `experience.registry.json`
- `lens.registry.json`
- `astronomy.catalog.index.json`
- `site.registry.index.json`
- `ui.registry.json`
- `build/lockfile.json` (or caller-provided lockfile path)

## Invariants
- Output ordering and hashes are deterministic.
- Refusal messages are deterministic and sorted.
- Cache hits must restore bitwise-identical outputs for identical input hash keys.

## Cross-References
- `tools/xstack/registry_compile/compiler.py`
- `tools/xstack/registry_compile/lockfile.py`
- `schemas/bundle_profile.schema.json`
- `tools/xstack/cache_store/store.py`
