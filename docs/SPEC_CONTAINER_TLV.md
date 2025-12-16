# Dominium TLV Container (DTLV) — Authoritative Serialization ABI

This document defines the **authoritative**, versioned, skip-friendly, deterministic container format used for **all public on-disk serialization** (saves, replays, packs/manifests, launcher config). It also defines the canonical TLV encoding rules used for ABI-treated blobs (e.g., net handshake payloads), whether carried inside a `DTLV` container or as standalone TLV streams.

The design goals are:

- **ABI stability**: readers must tolerate unknown chunks/records; writers must version everything.
- **Skip-unknown**: unknown chunk types and TLV tags can be skipped safely.
- **Determinism**: canonical hashing and canonical iteration rules are defined and reproducible.
- **Streaming**: readers do not require full-file load; writers can stream and finalize a directory.
- **Migration-first**: read-old/write-new with explicit migrations; no silent schema drift.

## 1. Terminology

- **Container**: a file starting with the `DTLV` header followed by one or more chunks and a directory.
- **Chunk**: a `(type_id, version)`-identified byte range in the file (payload), referenced by the directory.
- **Record**: a TLV entry inside a chunk payload: `(tag, len, payload_bytes)`.
- **TLV**: for this ABI, TLV uses fixed-width little-endian headers:
  - `tag` = `u32_le`
  - `len` = `u32_le`

## 2. Endianness and integer widths

- All integers in `DTLV` are **little-endian** on disk / over the wire.
- Readers must parse integers explicitly (no raw struct reads, no host-endian memcpy as ABI).
- Integer sizes are fixed: `u16` = 16-bit, `u32` = 32-bit, `u64` = 64-bit.

## 3. File header (DTLV v1)

All fields are little-endian.

| Offset | Size | Field | Meaning |
|---:|---:|---|---|
| 0 | 4 | `magic` | ASCII `"DTLV"` |
| 4 | 2 | `endian` | `0xFFFE` (little-endian marker) |
| 6 | 2 | `version` | container header version (currently `1`) |
| 8 | 4 | `header_size` | bytes of header (currently `32`) |
| 12 | 8 | `dir_offset` | absolute byte offset of directory from file start |
| 20 | 4 | `chunk_count` | number of directory entries |
| 24 | 4 | `dir_entry_size` | bytes per directory entry (currently `32`) |
| 28 | 4 | `flags` | reserved for future use (must be `0` for v1 writers) |

Notes:

- Readers must accept `header_size >= 32` and may skip unknown tail bytes in the header.
- `dir_offset` must point to the start of the directory; readers must bounds-check it.
- For v1 writers: `dir_entry_size` must be `32`.

## 4. Directory layout (DTLV v1)

The directory is an array of `chunk_count` entries at `dir_offset`.

Each directory entry is 32 bytes:

| Offset | Size | Field | Meaning |
|---:|---:|---|---|
| 0 | 4 | `type_id` | chunk type identifier (`u32_le`) |
| 4 | 2 | `version` | chunk schema version (`u16_le`) |
| 6 | 2 | `flags` | per-chunk flags (`u16_le`) |
| 8 | 8 | `offset` | absolute file offset of payload (`u64_le`) |
| 16 | 8 | `size` | payload size in bytes (`u64_le`) |
| 24 | 4 | `crc32` | optional CRC-32 of payload (`u32_le`, see flags) |
| 28 | 4 | `reserved` | must be `0` for v1 writers |

### 4.1. Directory safety rules

Readers must reject the container as malformed if any of the following hold:

- `dir_offset` is outside the file, or `dir_offset + chunk_count * dir_entry_size` exceeds file size.
- Any chunk payload range `(offset, size)` is outside the file.
- Any entry uses `dir_entry_size` that the reader does not support (v1 readers support `32`).

Overlapping chunks are not inherently invalid, but **writers must not create overlaps** and readers must not assume overlap-free unless explicitly validated.

### 4.2. Chunk type ID ranges

Chunk type IDs are ABI:

- `0x00000001..0x7FFFFFFF`: engine/product reserved (stable; do not renumber).
- `0x80000000..0xFFFFFFFF`: third-party/mod reserved.

## 5. Chunk payload encoding (TLV record stream)

For `DTLV` v1, chunk payload bytes are a **TLV record stream**:

```
repeat:
  u32_le tag;
  u32_le len;
  u8     payload[len];
```

### 5.1. Skip-unknown rules (records)

- Unknown `tag` values must be skipped by advancing `len` bytes.
- Readers must bounds-check: if `len` exceeds remaining payload bytes, the chunk is malformed and must be rejected safely.
- `len=0` is legal.

### 5.2. Deterministic record ordering

When a chunk is used for deterministic hashing/identity, record order must be canonical:

- Records are sorted by `(tag asc, payload_bytes lexicographic asc, len asc)` and then re-serialized in that order.
- Canonicalization is structural only; it does not interpret payload semantics.

Writers should emit canonical order for deterministic artifacts, but readers must not require it.

## 6. Skip-unknown rules (chunks)

- Unknown chunk `type_id` values must be ignored by readers (skip via directory range).
- Missing chunks are allowed unless a higher-level schema explicitly requires them.
- Unknown chunk versions must be rejected or migrated explicitly (no silent reinterpretation).

## 7. Canonical hashing (used by integrity + handshake)

This ABI defines a canonical **non-cryptographic** hash for schema/content identity: **FNV-1a 64-bit**.

- Offset basis: `14695981039346656037`
- Prime: `1099511628211`

### 7.1. Hash input encoding rules

- All numeric fields are hashed as their explicit little-endian byte encodings (`u16_le`, `u32_le`, `u64_le`).
- Never hash raw struct memory, pointers, or host-endian values.

### 7.2. Chunk hash

`chunk_hash64` is computed as:

1. Canonicalize the chunk payload TLV stream (Section 5.2) into `canon_bytes`.
2. Hash:
   - `type_id (u32_le)`
   - `version (u16_le)`
   - `canon_bytes` (exact bytes)

### 7.3. Container content hash (optional)

When a single container-wide identity is needed (e.g., for a manifest), hash the ordered list of chunk hashes:

- Sort directory entries by `(type_id asc, version asc)` for hashing order.
- Compute `chunk_hash64` for each entry in that order.
- Hash the sequence of `chunk_hash64 (u64_le)` values.

## 8. Migration policy

Serialization is ABI. Changes require explicit versioning and migration:

- **Read old, write new**: readers should accept older versions; writers always emit the latest container/chunk versions.
- **Explicit migrations**:
  - Each chunk type defines the supported version range.
  - If an older chunk version is accepted, a migration function must convert it to the latest in-memory representation (or latest on-disk payload form) explicitly.
  - Unknown chunk versions are rejected by default.
- Migrations must be deterministic and must not consult network/clock/external state.

## 9. Malformed input handling requirements

All readers must fail safely (no out-of-bounds reads/writes, no infinite loops):

- Reject containers with invalid header fields, impossible offsets/sizes, or unsupported versions.
- Reject TLV payloads whose lengths exceed the remaining bytes.
- For skip-unknown: skipping must never trust unvalidated lengths.
