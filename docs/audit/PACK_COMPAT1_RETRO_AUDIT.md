Status: DERIVED
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Derived From:
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/packs/PACK_COMPATIBILITY_MANIFEST.md`

# PACK-COMPAT1 Retro Audit

## Scope
PACK-COMPAT-1 hardens offline pack verification for Setup and Launcher without changing pack contents or simulation semantics.

## Existing Surfaces
- Setup CLI exists in `tools/setup/setup_cli.py` and already exposes deterministic descriptor output, transactional install flows, and manifest validation.
- Launcher CLI exists in `tools/launcher/launch.py` and already validates dist layout plus SessionSpec/lockfile compatibility before boot.
- Pack discovery occurs in `tools/xstack/pack_loader/loader.py`; it already attaches:
  - `pack.trust.json`
  - `pack.capabilities.json`
  - `pack.compat.json`
- PACK-COMPAT-0 validation exists in `src/packs/compat/pack_compat_validator.py`.
- MOD-POLICY-0 enforcement exists in `src/modding/mod_policy_engine.py`.
- GEO-9 overlay conflict dry-run logic exists in `src/geo/overlay/overlay_merge_engine.py`.
- Dist layout build currently copies packs, selected bundle, compiled registries, and lockfile/manifest, but not the full compatibility registries/schemas needed for portable offline verification.

## Gaps Identified
- No shared offline verification pipeline produces a deterministic compatibility report before Setup/Launcher operations.
- No first-class `pack_compatibility_report` schema exists.
- No first-class `pack_lock` schema exists for the runtime/offline validated lock surface.
- Setup lacks:
  - `setup verify`
  - `setup list-packs`
  - `setup build-lock`
  - `setup diagnose-pack`
- Launcher does not run pack verification before session start and has no `compat-status` command.
- Dist layout is not yet self-sufficient for offline compatibility validation because `schemas/`, `data/registries/`, and CompatX version metadata are not copied into portable output.

## Integration Targets
- Shared verifier:
  - `src/packs/compat/pack_verification_pipeline.py`
- Setup integration:
  - `tools/setup/setup_cli.py`
- Launcher integration:
  - `tools/launcher/launch.py`
- Dist portability:
  - `tools/xstack/packagingx/dist_build.py`

## Determinism Notes
- Pack enumeration must sort by `(pack_id, pack_version)`.
- Contract checks must use the pinned/default universe contract bundle, never inferred runtime behavior.
- Overlay conflict detection must reuse COMPAT-SEM-3 deterministic conflict enumeration in dry-run mode.
- Pack lock output must use canonical serialization and stable hashing.
