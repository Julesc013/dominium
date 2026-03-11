Status: CANONICAL
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none

# Content and Storage Model (STOR0 / LIB-0)

Status: binding.
Scope: content-addressable storage, linked vs portable instances, and deterministic export/import layout.

## Canonical Root Layout

Reusable artifacts live in a single content-addressable store rooted at:

```text
<root>/
  bin/
    engine/<build_id>/
    game/<build_id>/
    client/<build_id>/
    server/<build_id>/
    setup/<build_id>/
    launcher/<build_id>/
    tool.<name>/<build_id>/

  store/
    packs/<hash>/
    profiles/<hash>/
    blueprints/<hash>/
    system_templates/<hash>/
    process_definitions/<hash>/
    logic_programs/<hash>/
    view_presets/<hash>/
    resource_pack_stubs/<hash>/
    locks/<hash>/
    migrations/<hash>/
    repro/<hash>/

  instances/<instance_id>/
    instance.manifest.json
    overrides/
    saves/

  saves/<save_id>/
    save.manifest.json
    state.snapshots/
    patches/
    proofs/

  exports/
    <bundle_id>.bundle
```

## Identity Rules

- Reusable artifacts are immutable and content-addressed by canonical SHA-256.
- Hash identity is computed from canonical serialized content, never host path or timestamp.
- Directory names carry only ids and hashes; semantic meaning lives in manifests and payloads.
- Filesystem listing order is irrelevant; manifest ordering is canonical.

## Linked and Portable Instances

Instances use one of two storage topologies:

- `linked`: the instance manifest stores hash references plus a `store_root` locator. Reusable artifacts are resolved from the shared store and are not duplicated into the instance.
- `portable`: the instance manifest stores the same hashes plus `embedded_artifacts`. Required reusable artifacts are vendored under `embedded_artifacts/` so the instance is self-contained offline.

This topology flag is a storage declaration only. It is not a gameplay/runtime mode and does not bypass `docs/canon/constitution_v1.md` section A4.

## Compatibility and Adapters

- Existing path-based manifests and loaders remain supported as compatibility adapters.
- `capability_lockfile` paths remain non-authoritative legacy references; `pack_lock_hash` is authoritative for LIB-0 flows.
- LIB-4 shareable artifacts may embed their manifest directly in the payload or emit a manifest sidecar that pins the payload by `content_hash`.
- Legacy `data/` layouts remain loadable, but new reusable artifacts must resolve through CAS categories or explicit portable embeddings.

## Determinism Rules

- No CAS operation may depend on filesystem timestamps, network access, or platform-specific metadata.
- Export/import must preserve canonical file ordering and hash identity.
- Missing optional store artifacts must produce explicit refusal or explicit degraded mode, never silent fallback.

## Related Contracts

- `schema/lib/store_root.schema`
- `schema/lib/install_manifest.schema`
- `schema/lib/instance_manifest.schema`
- `schema/lib/save_manifest.schema`
- `schema/lib/artifact_manifest.schema`
- `schema/lib/artifact_reference.schema`
- `docs/architecture/SAVE_MODEL.md`
- `docs/architecture/INSTALL_MODEL.md`
- `docs/architecture/INSTANCE_MODEL.md`
- `docs/architecture/ARTIFACT_MODEL.md`
- `docs/architecture/BUNDLE_MODEL.md`
