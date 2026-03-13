Status: CANONICAL
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: RELEASE
Replacement Target: signed release manifest constitution after RELEASE-3

# Release Manifest Model

## Purpose

RELEASE-1 defines the deterministic manifest that describes a concrete distribution directory.
The release manifest enables:

- offline verification
- reproducible install inspection
- integrity checking of shipped binaries and content
- compatibility debugging across builds, packs, locks, and profiles

## Scope

- One release manifest exists per distribution directory.
- The manifest enumerates shipped artifacts only.
- The manifest is generated from deterministic local inputs only.
- The manifest does not require network access.

## Canonical Rules

### 1. Content Addressing

- Every artifact entry is content-addressed.
- `manifest_hash` is the canonical hash of the manifest body with `manifest_hash`, `deterministic_fingerprint`, and optional `signatures` blanked.
- `deterministic_fingerprint` is the canonical hash of the manifest with `deterministic_fingerprint` and optional `signatures` blanked after `manifest_hash` is populated.

### 2. Artifact Coverage

The manifest enumerates shipped:

- binaries
- packs
- profiles
- locks
- bundles
- manifests

For product binaries the manifest must record:

- binary content hash
- `build_id`
- endpoint descriptor hash

For pack artifacts the manifest must record:

- shipped pack artifact hash
- effective compatibility hash when available

### 3. Offline Verification

Verification operates only on:

- the distribution directory
- the release manifest
- deterministic local command execution for descriptor emission

Verification checks:

- every listed artifact exists
- content hashes match
- endpoint descriptors emitted by binaries match recorded descriptor hashes
- endpoint descriptor build metadata recomputes the recorded `build_id` when sufficient descriptor metadata is present
- pack compatibility hashes match shipped pack metadata when available
- optional detached or inline signatures verify deterministically when present

### 4. Optional Sections

Optional metadata may include:

- stability tagging report hash
- regression baseline hashes
- provisional-stub summaries
- optional signature blocks for detached/offline verification workflows

Optional metadata must not be required for offline verification unless the referenced artifacts are actually shipped.

### 5. Mix-and-Match Guarantee

- RELEASE rules must not bypass CAP-NEG.
- A release manifest is descriptive, not permissive.
- Interoperability remains governed by negotiation and semantic contract compatibility.

## Deterministic Ordering

- Artifact entries are sorted by `(artifact_kind, artifact_name)`.
- File tree hashing uses sorted forward-slash relative paths only.
- No timestamps, hostnames, usernames, or absolute paths participate in manifest identity.

## Verification Integration

- `setup verify --release-manifest <path>` must invoke the governed offline verifier.
- `launcher compat-status` must surface the release identity and manifest hash when a release manifest is present.

## Non-Goals

- signing
- packaging archive generation
- bitwise reproducible binary enforcement across toolchains
- network-based trust verification

## Readiness

- Ready for `RELEASE-2` signing hooks.
- Ready for `RELEASE-3` reproducible build comparison once the distribution wrappers stop deriving build metadata from live source state.
