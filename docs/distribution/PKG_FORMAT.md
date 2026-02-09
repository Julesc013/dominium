Status: DERIVED
Last Reviewed: 2026-02-08
Supersedes: none
Superseded By: none

# dompkg Container Format

## Scope

This document defines the binary `.dompkg` format used for distributable artifacts.
The package format is deterministic, content-addressable, and verification-first.
Canonical manifest encoding is TLV; JSON is an exported inspection view.

## Section Layout

Each package is:

1. Fixed header (`80` bytes)
2. Manifest TLV block
3. Chunk table block
4. Payload chunk blob block
5. Signature block (optional)

All integers are little-endian.
Offsets are absolute file offsets.

## Header Layout

The header is encoded as:

- `magic[8]`: ASCII `DOMPKG10`
- `header_size:u32`: currently `80`
- `format_version:u32`: currently `1`
- `manifest_tlv_offset:u64`
- `manifest_tlv_size:u64`
- `chunk_table_offset:u64`
- `chunk_table_size:u64`
- `payload_offset:u64`
- `payload_size:u64`
- `signature_offset:u64`
- `signature_size:u64`

Offsets are absolute file offsets.
The signature block may be empty (`offset=0`, `size=0`).

## Manifest Block (Canonical TLV)

The canonical manifest encoding is TLV.

TLV entry encoding:

- `type:u16`
- `length:u32`
- `value[length]:bytes`

Manifest TLV v1 uses:

- `type=1`: canonical JSON manifest payload (UTF-8 bytes)

The canonical JSON payload MUST be emitted with sorted keys, compact separators, and ASCII-safe encoding.
JSON export files are for inspection only and are not canonical package state.

## Chunk Table Format

The chunk table is a fixed-width record array.
Record size is `64` bytes.

Per-record encoding:

- `file_index:u32`
- `chunk_index:u32`
- `raw_offset:u64` (byte offset in logical file before chunking)
- `raw_size:u32`
- `compressed_size:u32`
- `payload_offset:u64` (offset from `payload_offset` header field)
- `raw_sha256[32]:bytes`

Chunk order is deterministic:

1. files sorted lexicographically by normalized path
2. chunks in increasing `raw_offset` order

## Payload Chunk Encoding

Chunking algorithm v1:

- Fixed chunk size: `1 MiB` (`1048576` bytes) raw
- Last chunk may be smaller
- `raw_sha256` is over raw bytes only

Compression:

- Default algorithm: Deflate
- Compression policy is pluggable
- zstd is optional and disabled by default
- Deflate support is mandatory

Payload chunk bytes are concatenated in chunk table order.

## Signature Block

Signature block is optional.

When present, it is UTF-8 JSON with signer metadata and detached signature payload references.
When absent, `signature_offset=0` and `signature_size=0`.
Signatures do not alter package identity.

## Content Identity

`content_hash` is computed over:

- header bytes with `signature_offset=0` and `signature_size=0`
- manifest TLV bytes
- chunk table bytes
- payload bytes

The signature block is excluded from `content_hash`.

## Determinism Requirements

Given identical input files and metadata:

- identical manifest TLV bytes
- identical chunk table bytes
- identical payload bytes
- identical `content_hash`

Package generation must not depend on wall clock, locale, process ordering, or non-deterministic file walking.

## Path and Compatibility Rules

- Paths are normalized to forward slashes (`/`)
- Relative paths only
- `..` segments are forbidden
- Duplicate normalized paths are forbidden
- Unknown manifest fields may be preserved in open maps

## Forward Compatibility

- Unknown TLV types MUST be skipped by length
- Unknown manifest fields MUST be preserved by tools that rewrite manifests
- `format_version` bump is required for binary layout changes

## Compression Policy

- Required support: `deflate`
- Optional support: `zstd` (disabled unless policy enables)
- Policy switch is external configuration and MUST be explicit
- Packages encoded with non-default compression MUST still include enough manifest data for verifier refusal diagnostics

## Failure Semantics

Verification and extraction MUST refuse loudly with stable reason codes:

- `refuse.invalid_header`
- `refuse.invalid_offsets`
- `refuse.invalid_manifest_tlv`
- `refuse.schema_invalid`
- `refuse.hash_mismatch`
- `refuse.signature_invalid`
- `refuse.signature_required`
