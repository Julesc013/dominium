Status: DERIVED
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `schemas/pack_manifest.schema.json` and `docs/architecture/pack_system.md`.

# Pack Substrate v1

## Purpose
Define canonical on-disk pack layout for deterministic discovery and validation tooling.

## Required Layout
- `packs/<category>/<pack_id>/pack.json`
- Allowed categories: `core`, `domain`, `experience`, `law`, `tool`
- Optional pack-local directories: `data/`, `assets/`, `ui/`, `scenarios/`

## Invariants
- No executable code is allowed under `packs/`.
- Pack activation is explicit and manifest-driven; no implicit runtime branching.
- Dependency and contribution validation is deterministic and refusal-based.

## Cross-References
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/architecture/pack_system.md`
- `docs/contracts/versioning_and_migration.md`
