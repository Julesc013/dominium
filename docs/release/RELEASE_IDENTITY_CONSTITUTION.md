Status: CANONICAL
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: RELEASE
Replacement Target: release-pinned build, manifest, and distribution constitution after RELEASE-1 artifact manifest generation

# Release Identity Constitution

This document freezes the deterministic release identity model for `v0.0.0` and forward-compatible release work.

## Versions

- `product_version` is `SemVer` in the form `major.minor.patch` with an optional deterministic build suffix `+<build_id>`.
- `release_tag` is `v<semver>-<channel>`.
- Release channels are limited to:
  - `mock`
  - `alpha`
  - `beta`
  - `rc`
  - `stable`
- Semantic contract registry versioning remains pinned separately from product versioning.

## Deterministic Build ID

`build_id` must be derived only from deterministic inputs:

- semantic contract registry hash
- compilation options hash
- source revision identifier, if available
- otherwise an explicit build number
- `product_id`
- platform ABI tag only when unavoidable

### Prohibited Build ID Inputs

The following must never participate in canonical build ID generation:

- wall-clock timestamps
- hostname
- username
- absolute paths
- machine-local temporary directories
- nondeterministic environment probes

### Build ID Format

- `build_id` format is `build.<sha256-prefix>`
- input fields must be ordered canonically before hashing
- when a source revision identifier is present, it supersedes fallback build numbering

## Artifact Identity

Artifacts must declare deterministic identity data.

Minimum fields:

- `artifact_kind`
- `content_hash`
- `build_id` for binaries and build-produced artifacts where relevant
- `contract_bundle_hash` for universe-bound artifacts where relevant
- `deterministic_fingerprint`

Artifact identity is content-addressed.
Host path placement is never authoritative identity.

## Reproducibility Rules

Given identical canonical inputs, two builds must produce identical:

- `build_id`
- endpoint descriptors
- release identity payloads
- artifact naming strings derived from content hash/build ID

Non-goal for `RELEASE-0`:

- bitwise identical binaries across all toolchains are desirable but not guaranteed

Required guarantee:

- semantic fingerprints, build IDs, contract hashes, and pack/content hashes must still match for equivalent inputs

## Mix-and-Match Guarantee

Products must not assume identical product versions or identical build IDs.

Interoperability is governed by CAP-NEG:

- descriptors remain authoritative for negotiation
- release identity does not bypass negotiation
- release identity does not authorize compatibility by itself

## Descriptor Integration Rule

Every emitted endpoint descriptor must include deterministic build identity.

For `v0.0.0`, this requirement is satisfied by:

- `product_version` carrying the `+<build_id>` suffix when no explicit version override is supplied
- `extensions.official.build_id`

Additional release metadata may appear in descriptor extensions, but must remain deterministic.

## Legacy Distribution Surface Note

Legacy distribution/build-manifest surfaces that still carry timestamps are not authoritative for canonical build ID generation.

They must be reconciled by later release packaging work and must not be treated as canonical build identity inputs.

## Change Control

This constitution may not change without:

- semantic contract review where interoperability meaning changes
- migration/refusal planning if persisted release artifacts are affected
- regression update tags where locked release baselines are impacted
