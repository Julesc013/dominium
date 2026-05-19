Status: DERIVED
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `contracts/schema/pack_manifest.schema.json` and `docs/architecture/pack_system.md`.

# Pack Substrate v1

## Purpose
Define canonical on-disk pack layout for deterministic discovery and validation tooling.

## Required Layout
- `content/packs/<category>/<pack_id>/pack.json`
- Allowed categories: `blueprint`, `core`, `derived`, `domain`,
  `example`, `experience`, `law`, `official`, `reality`, `representation`,
  `spec`, `tool`, and `worldgen`.
- Optional pack-local directories: `data/`, `assets/`, `docs/`, `ui/`,
  and `scenarios/`.

## Invariants
- No executable code is allowed under `content/packs/`.
- Pack activation is explicit and manifest-driven; no implicit runtime branching.
- Dependency and contribution validation is deterministic and refusal-based.

## Cross-References
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/architecture/pack_system.md`
- `docs/reference/contracts/versioning_and_migration.md`
