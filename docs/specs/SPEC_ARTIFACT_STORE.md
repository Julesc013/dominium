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
- None. Game consumes engine primitives where applicable.

TOOLS:
- Authoring/inspection utilities described here.
- Implementation lives under `tools/` (including shared tool runtime).

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
# Artifact Store (Launcher State)

This spec defines the launcher artifact store: a read-only, hash-addressed
content cache shared across instances.

## 1. Identity

Artifacts are identified by:
- strong content hash (SHA-256 in this revision)
- payload size in bytes
- content type (`engine|game|pack|mod|runtime`)
- optional opaque provenance metadata

Once verified, payloads are immutable.

## 2. Layout

The store lives under the launcher state root:

```
<state_root>/artifacts/
  sha256/
    <hash_hex>/
      artifact.tlv
      payload/
        payload.bin
```

Rules:
- `<hash_hex>` is lowercase hex of the SHA-256 digest (64 chars).
- `payload/payload.bin` is never modified after verification.
- Instances reference artifacts read-only by hash; instances never write into
  `artifacts/`.

## 3. Metadata (`artifact.tlv`)

`artifact.tlv` is a versioned TLV container (skip-unknown, forward-compatible).

Root fields:
- `schema_version` (u32): `1`
- `hash_bytes` (bytes): SHA-256 digest
- `size_bytes` (u64): payload size
- `content_type` (u32): `LauncherContentType`
- `timestamp_us` (u64): creation/import time
- `verification_status` (u32): `0 unknown | 1 verified | 2 failed`
- `source` (string, optional): opaque provenance/source data

Unknown tags:
- must be skipped on read
- must be preserved and re-emitted unchanged when rewriting metadata

## 4. Verification

Verification is deterministic:
- compute SHA-256 over `payload/payload.bin`
- compare computed hash to `artifact.tlv.hash_bytes`
- compare `payload` size to `artifact.tlv.size_bytes` when size is non-zero
- validate content type matches the referencing manifest entry type

No network fetch or signature verification is performed in this revision.