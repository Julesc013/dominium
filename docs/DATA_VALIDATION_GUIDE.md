# Data Validation Guide (DATA1)

This guide explains how to run validators and fix common failures.

## How to Run

### CLI (tooling)
```
data_validate --input=<path> --schema-id=<u64> --schema-version=MAJOR.MINOR.PATCH
```

### Tests
```
ctest -R engine_data_validate
```

## Common Failures and Fixes

### DATA-VALID-001 (Structural/Semantic)
- **Missing required field**: add the required TLV tag with a valid payload.
- **Invalid type/length**: ensure payload length matches the field type (u32=4, u64=8).
- **Out-of-range value**: clamp or correct numeric values to schema bounds.

### DATA-VALID-002 (Determinism/Performance)
- **Non-canonical tag order**: sort TLV records by tag.
- **Unbounded repeats**: add a schema max_count and keep repeats within bounds.
- **Missing LOD/fallback**: include required LOD or fallback tags.

### DATA-MIGRATE-001 (Migration)
- **Major version mismatch**: add a deterministic migration or refuse the data.
- **Version ahead/behind**: align schema versions or update compatibility metadata.

## Authoring Checklist

- Declare schema_id and semantic version.
- Keep tags stable and ordered deterministically.
- Enforce bounded list sizes.
- Include LOD and fallback tags when required by schema.
- Avoid float fields in authoritative schemas.
