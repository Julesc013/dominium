Status: CANONICAL
Last Reviewed: 2026-03-13
Stability: provisional
Future Series: RELEASE
Replacement Target: release-pinned artifact manifest and packaging naming contract after DIST packaging lanes are frozen

# Artifact Naming Rules

This document freezes deterministic artifact naming templates for `RELEASE-0`.

These are naming rules only.
They do not yet define packaging layout or archive structure.

## General Rules

- Names must be derived from canonical content hashes and deterministic build IDs only.
- Names must not include wall-clock timestamps, hostnames, usernames, or absolute paths.
- Hash prefixes use the first `12` lowercase hex characters of the canonical content hash unless a later release constitution replaces that rule.

## Naming Templates

### Binaries

Template:

- `<product_id>-<semver>+<build_id>-<platform_tag>`

Example shape:

- `client-0.0.0+build.ab7d7aaea59a92b1-platform.posix_min`

Notes:

- `semver` is the plain semantic version without an embedded channel.
- `build_id` is the deterministic release build ID.
- `platform_tag` is descriptive and does not replace content addressing.

### Packs

Template:

- `<pack_id>-<pack_version>-<pack_hash_prefix>`

### Locks

Template:

- `pack_lock-<hash_prefix>`

### Bundles

Template:

- `<bundle_kind>-<bundle_id>-<bundle_hash_prefix>`

### Manifests

Template:

- `manifest-<kind>-<hash_prefix>`

## Non-Goals

- No packaging extension policy is frozen here.
- No archive compression policy is frozen here.
- No installer naming or channel folder layout is frozen here.

Those concerns remain future release/distribution work.
