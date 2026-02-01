Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. Engine provides generic primitives only if referenced.

GAME:
- Rules, policy, and interpretation defined by this spec.
- Implementation lives under `game/` (rules/content/ui as applicable).

TOOLS:
- None. Tools may only consume public APIs if needed.

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
# Instance Model (Launcher State)

This spec defines the launcher instance system: isolated on-disk roots, a
reproducible TLV manifest lockfile, portability via import/export, and
deterministic manifest hashing.

## 1. Canonical instance root layout

All instance paths are rooted under a launcher-provided state root:

```
<state_root>/instances/<instance_id>/
  manifest.tlv
  payload_refs.tlv
  known_good.tlv
  config/
    config.tlv
  saves/
  mods/
  content/
  cache/
  logs/
    launch_history.tlv
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
- `payload_refs.tlv` is a derived index of resolved artifact payload references
  (hash/type/size/algo) used for verification and launch planning; it can be
  rebuilt deterministically from `manifest.tlv` and the artifact store.
- `known_good.tlv` is a pointer to the last known-good snapshot under
  `previous/` (used by rollback).
- `config/config.tlv` stores per-instance launcher overrides (separate from the manifest).
- `logs/launch_history.tlv` stores the last N launch attempts for recovery suggestions.

See `docs/specs/SPEC_LAUNCHER_PRELAUNCH_CONFIG.md` for configuration layering, safe mode, and recovery behavior.

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
  - `explicit_order_override` (i32, optional; per-pack load-order override used by deterministic resolution)

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

## 7. Transaction engine (install/update/remove/verify/repair/rollback)

Launcher instance mutations use an explicit transaction state machine with
staging-only writes:

Phases:
1. `prepare`: load live manifest, create `transaction.tlv` (transaction id).
2. `stage`: write new `staging/manifest.tlv`.
3. `verify`: verify referenced artifacts against the artifact store; write
   `staging/payload_refs.tlv`.
4. `commit`: atomic swap via rename; archive prior state under `previous/`.
5. `rollback`: discard staging on failure; live instance remains untouched.

Rules:
- All writes happen under `staging/` until `commit`.
- `commit` swaps `manifest.tlv` + `payload_refs.tlv` atomically at the file
  level (rename), and archives the prior live files under a deterministic
  directory name in `previous/`.
- `verify` must complete before `commit`.
- On any failure before `commit`, live state is untouched; staged state is
  recoverable or safely discarded.

Failure recovery:
- If `staging/transaction.tlv` exists at startup, the launcher may safely
  discard `staging/*` (no live state is modified).

Known-good snapshots + rollback:
- Successful `verify`/`repair` operations stage a snapshot directory under
  `staging/known_good_snapshot/` and a pointer file `staging/known_good.tlv`.
- At commit, the snapshot is moved under `previous/known_good_<hash>_<stamp>/`
  and `known_good.tlv` is swapped into place.
- `rollback_to_known_good` restores the snapshot manifest/payload references
  via the same transaction engine and records the source transaction id + cause
  in audit.