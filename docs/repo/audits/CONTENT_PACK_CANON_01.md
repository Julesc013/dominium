Status: DERIVED
Last Reviewed: 2026-05-20
Supersedes: none
Superseded By: none
Stability: provisional
Task: CONTENT-PACK-CANON-01

# CONTENT-PACK-CANON-01 Audit

## Scope

Normalize active authored-content pack and domain-content layout under `content/`.

Starting commit: `4869e035b`

Branch: `main`

## Chosen Pack Layout

`content/packs/<category>/<pack_id>/`

Allowed categories are recorded in `content/packs/README.md`:

- `blueprint`
- `core`
- `derived`
- `domain`
- `example`
- `experience`
- `law`
- `official`
- `reality`
- `representation`
- `spec`
- `tool`
- `worldgen`

## Pack Routes

- `content/packs/blueprints/` -> `content/packs/blueprint/`
- `content/packs/specs/` -> `content/packs/spec/`
- `content/packs/physics/physics.default.realistic/` -> `content/packs/domain/physics.default.realistic/`
- `content/packs/system_templates/base/` -> `content/packs/core/system_templates.base/`
- Flat `content/packs/org.dominium.base.*` and `org.dominium.core.*` packs -> `content/packs/core/`
- Flat `org.dominium.examples.*` packs -> `content/packs/example/`
- Flat `org.dominium.realities.*`, `org.dominium.earth.srtm`, and `org.dominium.sol.spice` packs -> `content/packs/reality/`
- Flat `org.dominium.worldgen.*` packs -> `content/packs/worldgen/`
- Remaining flat domain-like `org.dominium.*` packs -> `content/packs/domain/`

## Domain Content Routes

- `content/domains/game/core/astro/sol/` -> `content/domains/astronomy/sol/`
- `content/domains/game/core/cosmo/` -> `content/domains/cosmology/`
- `content/domains/game/core/mechanics/` -> `content/domains/mechanics/`
- `content/domains/game/core/README.md` -> `content/domains/README.game-core-migration.md`
- `content/domains/worldgen/real/*/content/*` -> `content/domains/worldgen/real/*/*`

## Identity Fields

Pack IDs, manifest IDs, compatibility fields, capability fields, trust files, and pack-local payload files were moved by path only. No semantic pack IDs or hashes were intentionally changed.

## References Updated

Active references to moved pack and domain paths were updated. Executable compatibility payload imports now point to `tools.validators.package.compatibility_payload`.

Generated and historical archive snapshots were not hand-edited.

## Validator Update

`tools/validators/repo/check_path_terms.py` now blocks the retired active content wrappers and pack category spellings covered by this pass.

## Validation Results

Pending final combined validation for the broader cleanup wave.

## Follow-Up Work

- Run package/content validators after the full path-map repair pass.
- Consider a dedicated pack manifest validator that enforces the category list from `content/packs/README.md`.
