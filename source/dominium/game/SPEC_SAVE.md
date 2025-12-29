# Save Spec (DMSG)

Status: v1
Version: 1

This document defines the Dominium game snapshot container `DMSG`.

## Endianness
- All numeric fields in the `DMSG` header and chunk records are little-endian.
- The endian marker is `0x0000FFFE` (u32_le).

## File header (DMSG v1)

| Offset | Size | Field | Meaning |
|---:|---:|---|---|
| 0 | 4 | `magic` | ASCII `"DMSG"` |
| 4 | 4 | `version` | container version (`1`) |
| 8 | 4 | `endian` | `0x0000FFFE` (little-endian marker) |
| 12 | 4 | `ups` | updates per second |
| 16 | 8 | `tick_index` | simulation tick |
| 24 | 8 | `seed` | world seed |
| 32 | 4 | `content_tlv_len` | bytes of content identity TLV |
| 36 | N | `content_tlv` | content identity TLV bytes |

Immediately after `content_tlv` comes the chunk stream.

## Content identity TLV

Format: repeated TLV records: `[tag:u32_le][len:u32_le][payload bytes]`.

Tags (v1):
- `0x0001` `PACKSET_ID` — `u64_le` FNV-1a hash of ordered pack/mod id+version strings.
- `0x0002` `PACK_HASH` — `u64_le` FNV-1a hash of each pack TLV blob; repeated.
- `0x0003` `MOD_HASH` — `u64_le` FNV-1a hash of each mod TLV blob; repeated.
- `0x0004` `INSTANCE_ID` — UTF-8 bytes of the instance id (no null terminator).

Notes:
- Missing tags are allowed if the data is unavailable.
- Hash inputs are canonical byte encodings (UTF-8 strings or TLV blob bytes).

## Chunk stream

Chunks are stored sequentially after the header.

Each chunk:
```
tag[4]        // fourcc ASCII
version u32   // chunk schema version
size u32      // payload size in bytes
payload[size]
```

## Required chunks

- `CORE` v1: authoritative simulation snapshot.
  - Payload is the legacy game world blob produced by `game_save_world_blob`
    (native-endian TLV with `TAG_INSTANCE` and `TAG_CHUNK` records; see
    `docs/DATA_FORMATS.md`).
- `RNG ` v1: deterministic RNG state.
  - Payload: `u32_le` of `d_rng_state.state`.

## Optional chunks

- `NET ` v1: lockstep session state (not required in v1).
- `META` v1: debug or provenance metadata (non-authoritative).

## Load policy

- Unknown chunk tags are skipped (forward-compatible).
- Known chunk with **higher** version than supported must fail with a
  “migration required” error.
- Missing required chunks or malformed lengths are fatal.

## Compatibility promise

`DMSG` is versioned; breaking changes require incrementing the container
version. Readers should accept older versions with explicit migrations and
never silently coerce newer data.
