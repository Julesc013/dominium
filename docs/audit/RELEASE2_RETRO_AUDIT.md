Status: DERIVED
Last Reviewed: 2026-03-13
Stability: provisional
Future Series: RELEASE
Replacement Target: supersede with signed distribution audit after RELEASE-3

# RELEASE-2 Retro Audit

## Scope

This audit reviews the current release identity and manifest surfaces before adding reproducibility checks and optional signing hooks.

## Current Version Strings

- Product descriptors carry `product_version` values shaped as `0.0.0+<build_id>`.
- Release identity is defined by `docs/release/RELEASE_IDENTITY_CONSTITUTION.md`.
- Release manifests derive `release_id` from `release_semver`, release channel, and the deterministic build-set hash.

## CAP-NEG Endpoint Descriptor Fields

Current descriptor emission includes:

- `extensions.official.build_id`
- `extensions.official.git_commit_hash`
- `extensions.official.semantic_contract_registry_hash`
- `extensions.official.compilation_options_hash`
- `extensions.official.product_capability_defaults_hash`
- `extensions.official.product_registry_row_hash`
- `extensions.official.platform_id`
- `extensions.official.platform_descriptor_hash`
- `extensions.official.platform_capability_ids`

Gap identified:

- descriptors do not yet expose enough build-input detail to recompute `build_id` offline from descriptor metadata alone

## Build ID Generation Logic

Current `src/release/build_id_engine.py` derives `build_id` from:

- `product_id`
- `semantic_contract_registry_hash`
- `compilation_options_hash`
- `source_revision_id` if available
- otherwise `explicit_build_number`
- `platform_tag`

Confirmed:

- no wall-clock timestamps participate in build ID generation
- no hostname or absolute path participates in build ID generation

Gap identified:

- build configuration and full build-input provenance are only indirectly visible through `compilation_options_hash`

## Artifact Naming Patterns

Current naming rules are documented in `docs/release/ARTIFACT_NAMING_RULES.md`.
They are deterministic and content-addressed, but there is not yet a dedicated reproducibility audit that compares one manifest against a second build of the same inputs.

## Manifest Formats

Current governed manifest-like surfaces:

- `dist/manifests/release_manifest.json`
- `dist/install.manifest.json`
- `dist/manifest.json`
- pack alias and compatibility manifests under `dist/packs/**`

Current RELEASE-1 manifest supports:

- binary hashes
- pack hashes
- profile / lock / bundle / manifest hashes
- semantic contract registry hash
- optional stability and regression hashes

Gap identified:

- optional signing blocks are not yet modeled
- manifest verification does not yet classify signature status
- build reproducibility is not yet cross-checked against a prior manifest

## Host-Dependent Metadata Review

No current governed release identity surface intentionally includes:

- wall-clock timestamps
- hostname
- absolute paths

Remaining risk areas to guard:

- future signature handling must not perturb `manifest_hash`
- future reproducibility tooling must compare canonical payloads only
