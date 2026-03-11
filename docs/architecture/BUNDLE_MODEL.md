Status: CANONICAL
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none

# Bundle Model (SHARE0 / LIB-0)

Status: binding.
Scope: deterministic share bundles for saves, replays, blueprints, modpacks, and instances.

## Bundle Types

- `save`
- `replay`
- `blueprint`
- `modpack`
- `instance`

## Instance Bundle

Instance bundles are the LIB-0 portable interchange primitive.

- Primary artifact: `instance/instance.manifest.json`
- Required lock payload: `instance/lockfiles/capabilities.lock`
- Required embedded artifacts: pack lock, profile bundle, and all pinned pack artifacts needed for portable replay/import
- Optional binaries may be added later without changing the bundle identity rules

## Determinism Rules

- Bundle contents are indexed canonically.
- File hashes must validate on inspect/import.
- Export/import must not depend on filesystem timestamps or OS metadata.
- Missing required embedded artifacts are refusal outcomes.

## Import Rules

- Portable import preserves embedded artifacts inside the imported instance.
- Linked import inserts embedded artifacts into the destination store and rewrites the instance manifest to `mode=linked`.
- Missing packs may degrade save/replay/modpack bundles, but portable instance bundles must be self-contained.

## Related Contracts

- `schema/bundle.container.schema`
- `docs/architecture/CONTENT_AND_STORAGE_MODEL.md`
- `docs/architecture/INSTANCE_MODEL.md`
