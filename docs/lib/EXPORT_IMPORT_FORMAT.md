Status: CANONICAL
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none

# EXPORT_IMPORT_FORMAT

Status: binding.
Scope: deterministic clone/export/import bundle doctrine for instances, saves, packs, and modpacks.

## Purpose

LIB-6 defines the user-facing interchange contract for:

- cloning instances locally
- exporting and importing instances
- exporting and importing saves
- exporting and importing packs
- exporting and importing modpack bundles

All bundle operations are offline-first, deterministic, and hash-verified.

## Bundle Kinds

Canonical bundle kinds:

- `bundle.instance.portable`
- `bundle.instance.linked`
- `bundle.save`
- `bundle.pack`
- `bundle.modpack`

Semantics:

- `bundle.instance.portable` contains a runnable portable instance payload.
- `bundle.instance.linked` contains a linked instance manifest plus the reusable artifacts required to re-materialize or verify it.
- `bundle.save` contains a save manifest plus save state payload, patches, and optional vendored pack artifacts.
- `bundle.pack` contains a single pack payload plus pack compat/lock metadata required for offline verification.
- `bundle.modpack` contains an instance-like pack set export with referenced pack artifacts and lock metadata.

## Canonical Directory Layout

Every canonical bundle directory uses this layout:

```text
<bundle_root>/
  bundle.manifest.json
  content/
    ...
  hashes/
    content.sha256.json
```

Rules:

- `bundle.manifest.json` is canonical JSON with sorted keys.
- `content/` holds all exported payload files.
- `hashes/content.sha256.json` is the ordered content-hash index for every exported item.
- Relative paths inside the bundle always use `/`.
- Directory listing order is irrelevant; manifest and hash index ordering are authoritative.

## Canonical Item Rules

Each exported item is represented by a canonical bundle item row:

- `item_kind`
- `item_id_or_hash`
- `relative_path`
- `content_hash`
- `deterministic_fingerprint`

Bundle items are ordered lexicographically by:

1. `relative_path`
2. `item_kind`
3. `item_id_or_hash`

## Bundle Hash Rule

`bundle_hash` is computed from the canonical ordered item-hash projection only.

Canonical projection:

- take the ordered bundle item rows for every file under `content/`
- project each row to `item_kind`, `item_id_or_hash`, `relative_path`, and `content_hash`
- canonical-serialize the ordered list
- compute SHA-256

Consequences:

- filesystem timestamps do not affect `bundle_hash`
- archive container metadata does not affect `bundle_hash`
- `bundle.manifest.json` does not participate in `bundle_hash`; it records the hash instead of defining it

## Verification Rules

Import and standalone verification must:

1. parse `bundle.manifest.json`
2. parse `hashes/content.sha256.json`
3. verify that the ordered item rows in both files match
4. recompute each `content_hash`
5. recompute `bundle_hash`
6. refuse if any mismatch occurs

No silent repair is permitted.

## Compatibility Checks

Instance import must run:

1. instance manifest validation
2. pack compat verification
3. provides resolution verification
4. capability negotiation preview
5. save-reference portability checks

Save import must run:

1. save manifest validation
2. contract bundle presence/hash validation
3. pack lock validation
4. migration or read-only policy preview when needed

Pack import must run:

1. pack manifest presence checks
2. pack compat validation
3. namespace/provides validation
4. CAS insertion verification

## Portable and Linked Modes

Portable exports:

- vendor required reusable artifacts into `content/`
- remain self-contained offline
- keep authoritative references by hash even when payloads are vendored

Linked exports:

- preserve linked instance/install references
- still include enough bundle metadata and reusable artifacts to validate/import offline
- may re-materialize artifacts into a destination store during import

## Archive Projection

The canonical LIB-6 representation is the bundle directory.

Optional archive projection may be used for transport if it preserves the exact directory contents.

Allowed deterministic archive projection:

- `zip` with fixed timestamp `2000-01-01T00:00:00Z`, normalized permissions, no extra fields, and lexicographically ordered entries

No OS-specific metadata is permitted in archive entries.

## Refusal Rules

Import must refuse when:

- `bundle_hash` mismatches
- any item `content_hash` mismatches
- bundle structure is incomplete
- required pack compat validation fails
- required provides resolution is missing or ambiguous under the active policy
- required save/install/instance manifests fail validation

No silent migration or silent provider selection is permitted.
