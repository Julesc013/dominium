Status: DERIVED
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: RELEASE
Replacement Target: release-pinned versioning and artifact identity baseline after RELEASE-1 manifest generation

# RELEASE-0 Retro Audit

## Scope

This audit covers the current release-identity-related surfaces before the `RELEASE-0` constitution is frozen:

- product version strings
- CAP-NEG endpoint descriptor build metadata
- build ID generation logic
- artifact naming patterns
- manifest surfaces carrying build identity

## Current Product Version Strings

The governed product defaults currently come from `data/registries/product_registry.json` `record.products[*].extensions.official.default_semver`.
Observed values are currently uniform:

- `client`: `0.0.0`
- `engine`: `0.0.0`
- `game`: `0.0.0`
- `launcher`: `0.0.0`
- `server`: `0.0.0`
- `setup`: `0.0.0`
- `tool.attach_console_stub`: `0.0.0`

Current distribution-facing binary aliases come from `extensions.official.dist_bin_names`.
There is not yet a single release constitution that defines how semver, build IDs, channels, and artifact names combine.

## CAP-NEG Endpoint Descriptor Surface

Current endpoint descriptors are emitted from:

- `src/compat/descriptor/descriptor_engine.py`
- `src/compat/capability_negotiation.py`

Descriptor-required top-level fields currently include:

- `product_id`
- `product_version`
- `protocol_versions_supported`
- `semantic_contract_versions_supported`
- `feature_capabilities`
- `required_capabilities`
- `optional_capabilities`
- `degrade_ladders`
- `deterministic_fingerprint`
- `extensions`

Release/build identity is currently carried through descriptor extensions:

- `official.build_id`
- `official.git_commit_hash`
- `official.semantic_contract_registry_hash`
- `official.compilation_options_hash`
- `official.product_capability_defaults_hash`
- `official.product_registry_row_hash`
- platform metadata fields added by APPSHELL/PLATFORM

This means descriptors already expose deterministic build identity, but the contract is implicit rather than frozen in a dedicated release constitution.

## Current Build ID Generation Logic

Current build ID generation lives in:

- `src/compat/descriptor/descriptor_engine.py`

The current seed is deterministic and derived from:

- `product_id`
- semantic contract registry hash
- compilation options hash
- git commit hash, if available
- otherwise fixed build number from `DOMINIUM_FIXED_BUILD_NUMBER` or default `0`

Current format:

- `build.<sha256-prefix>`

## Wall-Clock / Host Metadata Audit

### Build ID path

No wall-clock timestamps were found in the current build ID seed path.

No hostname or absolute-path metadata were found in the current build ID seed path.

### Release-adjacent legacy surfaces

Legacy distribution/build surfaces still contain timestamp-oriented metadata outside the canonical build ID path:

- `schema/distribution/build_manifest.schema`
  - requires `build_timestamp_utc`
- `tools/distribution/build_manifest.py`
  - uses `datetime.datetime.utcnow()`

These surfaces are packaging-oriented legacy artifacts and are not currently authoritative inputs to CAP-NEG build identity.
They must be reconciled in a later release-manifest task rather than silently folded into the deterministic build ID model here.

## Existing Artifact Naming Patterns

Observed current naming patterns are fragmented:

- product binary aliases are declared in `data/registries/product_registry.json`
- install manifests pin `product_builds` by `build_id`
- LIB artifact manifests use `artifact_kind_id` + `content_hash`
- repro/save/bundle/install manifests already carry build IDs or content hashes

There is not yet a single naming constitution for:

- binaries
- packs
- locks
- bundles
- manifests

## Existing Manifest Surfaces

Current manifest-like surfaces related to release identity include:

- `schema/lib/install_manifest.schema`
- `schema/lib/artifact_manifest.schema`
- `schema/lib/product_build_descriptor.schema`
- `schema/diag/repro_bundle_manifest.schema`
- `schema/distribution/build_manifest.schema`

Current state:

- LIB and DIAG surfaces are already content-addressed and deterministic in intent.
- Distribution naming/build metadata is not yet frozen under a release constitution.
- Build identity is present, but not yet governed by a dedicated release schema/registry set.

## Audit Conclusion

Safe insertion point for `RELEASE-0`:

- keep current deterministic build ID behavior
- move the build ID contract into a dedicated release engine
- keep endpoint descriptors emitting `build_id`
- formalize artifact identity and naming separately from packaging
- treat timestamp-bearing distribution manifest surfaces as legacy/release-follow-up work

No current evidence was found that canonical build IDs depend on:

- wall-clock time
- hostname
- absolute paths

The primary gap is governance and consistency, not determinism failure.
