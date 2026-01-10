# SPEC_CORE_DATA_PIPELINE — Authoring to TLV Packs

Status: draft  
Version: 1

## Scope
Defines the deterministic pipeline from `/data/core` authoring sources to
runtime TLV packs.

## Authoring formats
- JSON and TOML are preferred authoring formats.
- Lua is permitted **only at compile time** for deterministic generation.
- Runtime code MUST NOT execute authoring scripts.

## `coredata_compile` responsibilities
- Schema validation against authoritative core-data specs.
- Canonical ordering of entities and references.
- Deterministic TLV emission.
- Manifest and hash emission for identity binding.

## Output layout
Compiled packs are emitted under the canonical pack root:
- `<output_root>/<pack_id>/<version_8digit>/pack.tlv`
- `<output_root>/<pack_id>/<version_8digit>/pack_manifest.tlv`

Notes:
- `output_root` defaults to `repo/packs` at the repository root.
- `version_8digit` is the zero-padded numeric pack version (e.g., `00000001`).
- The compiler is responsible for creating intermediate directories.

## Pack format
- `pack.tlv` is a TLV stream of records (`u32_le tag` + `u32_le len`).
- Each record payload is itself a TLV stream of fields (see per-schema specs).
- A `PACK_META` record (`type_id = 0x00000001`) appears once and includes:
  - pack schema version
  - pack id
  - pack version (numeric + optional string)
  - content hash
- The content hash is computed over record hashes in canonical order and
  excludes the `PACK_META` record itself.

## Determinism guarantees
- Identical inputs MUST produce byte-identical TLV outputs.
- Canonical ordering MUST be stable across platforms.
- Hashing MUST be stable and reproducible.

## Error handling (refusal-first)
Compilation MUST refuse on:
- schema violations
- ambiguous or duplicate IDs
- unresolved references
- non-deterministic ordering

Runtime load MUST refuse on:
- missing required chunks
- schema version mismatch without migration
- identity digest mismatch

## Versioning and migrations
- Every schema is versioned.
- TLV pack versions advance when schema changes.
- Migration paths MUST be explicit; no best-effort upgrades.

## Related specs
- `docs/SPEC_CORE_DATA.md`
- `docs/SPEC_COSMO_CORE_DATA.md`
