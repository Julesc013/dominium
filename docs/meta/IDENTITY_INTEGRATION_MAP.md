Status: DERIVED
Last Reviewed: 2026-03-14
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: UNIVERSAL-ID
Replacement Target: release-pinned universal identity contract bundle and artifact identity registry

# Identity Integration Map

## Integration Rule
`universal_identity_block` is additive and must remain a sibling field. Existing payloads remain loadable when the field is absent.

Current repository state:
- generator/runtime paths may emit the block now
- checked-in persisted artifacts may still omit the block under the v0.0.0-mock warn-only migration policy

## Target Surfaces

### Updated in UNIVERSAL-ID0
- `release_manifest.json`
  - status: integrated
  - kind: `identity.suite_release`
- `release_index.json`
  - status: integrated
  - kind: `identity.suite_release`
- `install.manifest.json`
  - status: integrated for new generators; optional in validators
  - kind: `identity.install`
- `instance.manifest.json`
  - status: integrated for dist/default instance generation; optional in validators
  - kind: `identity.instance`
- `save.manifest.json`
  - status: validator-ready; optional for legacy payloads
  - kind: `identity.save`
- `pack_lock` payloads
  - status: integrated for runtime and library generators
  - kind: `identity.bundle`
- profile bundle payloads
  - status: integrated for runtime and library generators
  - kind: `identity.bundle`
- repro bundle manifest
  - status: integrated
  - kind: `identity.repro_bundle`
- negotiation record
  - status: integrated
  - kind: `identity.manifest`

### Validator / Warning Coverage Only in v0.0.0-mock
- `pack.compat.json`
  - status: optional block, warning if absent
  - kind: `identity.pack`
- pack manifests and adjacent bundle-like metadata
  - status: optional block, warning if absent
  - kind: inferred from artifact family

## Strictness Policy
- v0.0.0-mock
  - missing block: warning
  - malformed or mismatched block: refusal
- v0.0.1+
  - missing block: planned strict enforcement
