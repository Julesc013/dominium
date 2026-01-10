# COREDATA_BUILD — coredata_compile usage

This document describes how to compile `/data/core` authoring files into
deterministic TLV packs.

## Tool
`coredata_compile` is a standalone, offline compiler. It reads TOML sources
under `/data/core` and emits a versioned pack plus a deterministic manifest.

## Usage
Examples (from repo root):

```
coredata_compile --input-root=data/core --output-pack-id=base_cosmo --output-version=1
```

Custom output location:

```
coredata_compile --output-root=repo/packs --output-pack-id=base_cosmo --output-version=1
```

## Output layout
The compiler emits:
- `repo/packs/<pack_id>/<version_8digit>/pack.tlv`
- `repo/packs/<pack_id>/<version_8digit>/pack_manifest.tlv`

`version_8digit` is a zero-padded numeric pack version (e.g., `00000001`).

## Version parsing
`--output-version` accepts:
- numeric values (`1`, `42`)
- semver-like values (`1.2.3`)

Semver values are mapped to a numeric pack version as:

```
numeric = (major * 10000) + (minor * 100) + patch
```

## Format support
Current implementation supports TOML only. JSON support will be added later when
a deterministic parser is available in-tree.

## Determinism guarantees
- Identical inputs produce byte-identical `pack.tlv` and `pack_manifest.tlv`.
- Ordering is canonicalized by stable ID and record type.
- Unknown fields are refused unless explicitly declared non-sim metadata.

See:
- `docs/SPEC_CORE_DATA_PIPELINE.md`
- `docs/SPEC_CORE_DATA.md`
