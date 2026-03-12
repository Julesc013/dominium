Status: CANONICAL
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Bundle Model (SHARE0 / LIB-2)

Status: binding.
Scope: deterministic share bundles for saves, replays, blueprints, modpacks, and instances.

## Bundle Types

- `save`
- `replay`
- `blueprint`
- `modpack`
- `instance`

## Shareable Artifact Bundle

Blueprint bundles are the first LIB-4 shareable artifact bundle surface.

- Primary payload: `artifacts/blueprint/<payload>.json`
- Required sidecar: `artifacts/blueprint/shareable.artifact.manifest.json`
- The sidecar pins `content_hash`, contract/capability requirements, degrade mode, and migration refs
- Inspect/import must validate the sidecar before accepting the bundle

## Instance Bundle

Instance bundles are the LIB-2 portable interchange primitive.

- Primary artifact: `instance/instance.manifest.json`
- Required lock payload: `instance/lockfiles/capabilities.lock`
- Required embedded artifacts: pack lock, profile bundle, and all pinned pack artifacts needed for portable replay/import
- Optional embedded binaries may be carried through `embedded_builds`
- Save associations (`save_refs`) may be preserved, but save payloads must not be embedded in the instance bundle

## Determinism Rules

- Bundle contents are indexed canonically.
- File hashes must validate on inspect/import.
- Shareable artifact sidecars must validate `content_hash` against the bundled payload.
- Export/import must not depend on filesystem timestamps or OS metadata.
- Missing required embedded artifacts are refusal outcomes.

## Import Rules

- Portable import preserves embedded artifacts inside the imported instance.
- Portable import preserves `save_refs` and embedded build descriptors.
- Linked import inserts embedded artifacts into the destination store and rewrites the instance manifest to `mode=linked`.
- Linked import clears `embedded_artifacts` and `embedded_builds` from the imported manifest.
- Missing packs may degrade save/replay/modpack bundles, but portable instance bundles must be self-contained.

## Related Contracts

- `schema/bundle.container.schema`
- `schema/lib/artifact_manifest.schema`
- `docs/architecture/CONTENT_AND_STORAGE_MODEL.md`
- `docs/architecture/INSTANCE_MODEL.md`
- `docs/architecture/ARTIFACT_MODEL.md`
