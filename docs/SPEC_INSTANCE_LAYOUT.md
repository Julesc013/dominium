# Instance Model (Launcher State)

This spec defines the launcher instance system: isolated on-disk roots, a
reproducible TLV manifest lockfile, portability via import/export, and
deterministic manifest hashing.

## 1. Canonical instance root layout

All instance paths are rooted under a launcher-provided state root:

```
<state_root>/instances/<instance_id>/
  manifest.tlv
  config/
  saves/
  mods/
  content/
  cache/
  logs/
  staging/
  previous/
```

Rules:
- `<instance_id>` is a stable string identifier (UUID/string) and is the
  directory name.
- All mutable state is contained inside the instance root.
- No global shared mutable directories are permitted.
- Artifact payloads may be referenced read-only (by hash), but are never written
  in-place.

## 2. Manifest (`manifest.tlv`) — reproducible lockfile

The manifest is a versioned TLV container that must be safely round-trippable:
unknown fields are preserved and emitted unchanged when writing a manifest.

Required fields:
- `instance_id` (stable string)
- `creation_timestamp` (microseconds since epoch)
- `pinned_engine_build_id` (string; may be empty for templates)
- `pinned_game_build_id` (string; may be empty for templates)

Content graph (ordered list, order is significant):
- `content_entries[]`:
  - `type` (`engine|game|pack|mod|runtime`)
  - `id` (string)
  - `version` (string)
  - `hash_bytes` (opaque; empty when not pinned to a payload)
  - `enabled` (0/1)
  - `update_policy` (`never|prompt|auto`)

State markers:
- `known_good` (0/1)
- `last_verified_timestamp` (microseconds since epoch)
- `previous_manifest_hash` (optional)

Provenance (for cloning/import):
- Imported instances receive a new `instance_id` but preserve provenance by
  recording the source instance id and source manifest hash.

## 3. Deterministic hashing (reproducibility contract)

The manifest hash is computed from a canonical manifest serialization:
- TLV is written in a fixed, explicit tag order for known fields.
- `content_entries[]` are emitted in their stored order; no sorting is applied.
- Unknown TLV fields are preserved and re-emitted (root and per-entry).
- The hash is stable across platforms and must not depend on filesystem
  enumeration ordering.

Hash algorithm:
- `manifest_hash64 = FNV-1a64(canonical_manifest_tlv_bytes)`

Changing any serialized bytes (including reordering entries) changes the hash.

## 4. Lifecycle operations (no in-place mutation)

All instance mutations occur via `staging/` and atomic swap/rename:
- Live `manifest.tlv` is never modified in place.
- On success, the staged manifest becomes live.
- On failure, the live instance is left untouched.
- `previous/` retains prior state (including last known-good manifests).

Operations:
- `create_instance`: creates the full root layout and an initial manifest.
- `delete_instance`: soft delete only (moves state into `previous/`).
- `clone_instance`: duplicates manifest + config into a new isolated root (no
  shared mutable directories); records provenance.
- `template_instance`: produces a baseline manifest with payload references
  removed (hashes cleared) and state markers reset.
- `mark_known_good` / `mark_broken`: writes a new manifest via `staging/` and
  archives the prior live manifest under `previous/`.

## 5. Import / export (portability)

Export modes:
- Definition-only: `manifest.tlv` + `config/`.
- Full bundle: definition plus optional payloads, addressed by hash.

Full-bundle layout:
```
<export_root>/
  manifest.tlv
  config/
    config.tlv
  payloads/
    <hex(hash_bytes)>.bin
```

Import rules:
- Payload hashes in bundles use `hash_bytes` as an 8-byte little-endian
  `FNV-1a64(payload_bytes)` (other encodings are treated as incompatible unless
  `safe_mode=1`).
- Hashes are validated when payloads are present.
- Imports refuse incompatible bundles unless `safe_mode` is explicitly enabled
  (payloads are optional; when present their bytes must match the referenced
  hash).
- Imported instances receive a new `instance_id` and record provenance.

## 6. Audit integration

Every instance operation emits an audit record with:
- `instance_id`
- operation type
- result (ok/fail) and reason code
- manifest hashes (before/after where applicable)
