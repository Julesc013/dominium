Status: DERIVED
Last Reviewed: 2026-03-14
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: UNIVERSAL-ID
Replacement Target: release-pinned universal identity contract bundle and artifact identity registry

# Universal Identity Model

## Purpose
Define one canonical identity grammar for artifacts, manifests, formats, protocols, installs, instances, saves, releases, and repro bundles.

## UniversalIdentityBlock
`universal_identity_block` is a canonical sibling object embedded in governed artifacts.

Required fields:
- `identity_kind_id`
- `identity_id`
- `stability_class_id`
- `deterministic_fingerprint`
- `extensions`

Optional fields:
- `content_hash`
- `semver`
- `build_id`
- `format_version`
- `schema_version`
- `protocol_range`
- `contract_bundle_hash`

## Identity Kinds
- `identity.suite_release`
- `identity.product_binary`
- `identity.pack`
- `identity.bundle`
- `identity.protocol`
- `identity.schema`
- `identity.format`
- `identity.install`
- `identity.instance`
- `identity.save`
- `identity.manifest`
- `identity.repro_bundle`

## Rules

### Content Addressing
- Content-addressed artifacts must carry `content_hash`.
- `content_hash` is computed from canonical serialized artifact content with:
  - `deterministic_fingerprint` blanked
  - `universal_identity_block` removed from the hash seed

### Binary Identity
- Product binaries must carry `build_id`.
- Binary identity is represented through release/install identity surfaces and descriptor-backed metadata.

### Universe-Bound Artifacts
- Universe-bound artifacts must carry `contract_bundle_hash`.
- Saves and repro bundles are universe-bound by default.

### Protocol Surfaces
- Protocol artifacts must carry `protocol_range`.
- Negotiation records may also embed `protocol_range` even when their `identity_kind_id` is `identity.manifest`.

### Schema / Format Surfaces
- Schema artifacts use `content_hash` as the schema hash and must also carry `schema_version`.
- Format-bound artifacts must carry `format_version`.

### Canonical Serialization
- All identity blocks are canonically serialized with sorted keys.
- `deterministic_fingerprint` is computed with the fingerprint field blanked.
- Extensions are open-map but must serialize deterministically.

## Kind-Specific Minimum Requirements
- `identity.pack`
  - `content_hash`
  - `semver`
- `identity.product_binary`
  - `content_hash`
  - `build_id`
- `identity.save`
  - `contract_bundle_hash`
  - `format_version`
- `identity.protocol`
  - `protocol_range`
- `identity.schema`
  - `content_hash`
  - `schema_version`

## v0.0.0-mock Policy
- Existing artifacts may omit the block.
- Missing blocks are warnings in v0.0.0-mock.
- Malformed blocks, non-namespaced ids, or canonicalization mismatches are validation failures.
