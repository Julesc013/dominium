Status: DERIVED
Last Reviewed: 2026-03-14
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: UNIVERSAL-ID
Replacement Target: release-pinned universal identity contract bundle and artifact identity registry

# UNIVERSAL-IDENTITY-0 Retro Audit

## Scope
- RELEASE identity fields
- PACK-COMPAT / pack surfaces
- LIB install / instance / save surfaces
- CAP-NEG negotiation records
- DIAG repro bundle manifests
- distribution / update manifests

## Existing Identity Surfaces
- `build_id`
  - RELEASE build identity for binaries and endpoint descriptors
- `content_hash`
  - RELEASE artifact identities and store artifacts
- `pack_id` / `pack_version`
  - pack and pack compatibility manifests
- `protocol_version` / protocol ranges
  - CAP-NEG endpoint descriptors, negotiation records, install manifests, release indices
- `schema_version`
  - schema-governed manifests and registries
- `format_version`
  - save, pack lock, profile bundle, release manifest surfaces
- `contract_bundle_hash` / `semantic_contract_registry_hash`
  - universe-bound artifacts, releases, installs, saves
- `manifest_hash`
  - release manifests
- `endpoint_descriptor_hash`
  - install manifests and release manifests
- `bundle_hash`
  - repro bundles

## Drift / Duplication
- Similar identity semantics appear under different field names across release, library, pack, and repro layers.
- Content-addressing rules are consistent in practice but not expressed through a single embedded grammar.
- Some artifacts carry creator/build identity but not a unified namespaced artifact identity.
- Negotiation records and repro bundle manifests are deterministic, but their identity metadata is implicit rather than standardized.

## Artifacts Lacking a Consistent Embedded Identity Block
- `release_manifest.json`
- `release_index.json`
- `pack.compat.json`
- `install.manifest.json`
- `instance.manifest.json`
- `save.manifest.json`
- pack lock payloads
- profile bundle payloads
- repro bundle manifests
- negotiation records

## Safe Insertion Point
- Add a sibling field named `universal_identity_block`.
- Do not wrap existing payloads or rename current fields.
- Preserve existing loader behavior when the field is absent.
- Validate and canonicalize the block only when present during v0.0.0-mock.

## Compatibility Assessment
- Additive-only integration is safe for existing loaders.
- Existing deterministic fingerprints remain valid for legacy artifacts that omit the new block.
- New generators can emit the block and recompute artifact fingerprints without changing runtime semantics.
