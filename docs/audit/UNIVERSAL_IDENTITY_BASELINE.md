Status: DERIVED
Last Reviewed: 2026-03-14
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: UNIVERSAL-ID
Replacement Target: contract-pinned universal identity enforcement after v0.0.0-mock

# Universal Identity Baseline

## Identity Kinds

- `identity.bundle`
- `identity.format`
- `identity.install`
- `identity.instance`
- `identity.license_capability`
- `identity.manifest`
- `identity.pack`
- `identity.product_binary`
- `identity.protocol`
- `identity.repro_bundle`
- `identity.save`
- `identity.schema`
- `identity.suite_release`

## Required Fields Per Kind

- `identity.pack`: `content_hash`, `semver`
- `identity.product_binary`: `content_hash`, `build_id`
- `identity.save`: `contract_bundle_hash`, `format_version`
- `identity.protocol`: `protocol_range`
- `identity.schema`: `content_hash`, `schema_version`

## Integration Status

- Artifacts scanned: `59`
- Embedded identity blocks present: `59`
- Missing-block warnings: `0`
- Current policy: missing blocks warn in `v0.0.0-mock`; malformed blocks refuse

## Readiness

- Universal identity validator is ready for `validate.identity`
- Major distribution/update/trust manifests can embed `universal_identity_block` additively
- DIST-7 packaging can carry identity blocks in shipped manifests without changing runtime semantics
