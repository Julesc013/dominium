# TLV Schema Governance

## Scope
This document defines the rules for versioned TLV schemas used across Dominium/Domino
boundaries and the contract tests that enforce them.

## Schema Registry
- Schema IDs are centralized in `include/dominium/core_tlv_schema.h` and are append-only.
- Each entry defines `current_version`, `min_version`, and `max_version`.
- Validators must be deterministic and skip-unknown safe.
- Migration hooks are registered per schema; identity migrations are permitted.

## Versioning Rules
- Increment the schema version only when:
  - a required field is added or removed
  - a field’s semantic meaning changes
  - validation rules change in a way that affects acceptance
- Optional/unknown tags can be added without a version bump.
- Readers must accept versions in `[min_version, max_version]` when safe.
- If the on-disk version is too new or unsupported, return a stable `err_t` with
  `ERRD_TLV` and `ERRF_NOT_SUPPORTED | ERRF_POLICY_REFUSAL`.

## Canonical Encoding
- Launcher TLV is `{u32 tag, u32 len, payload}` with little-endian integers.
- DSK TLV uses the DSK header + `{u16 type, u32 len, payload}` records.
- Writers must output deterministic ordering and stable encoding.
- Readers must enforce bounds and skip unknown tags without failure.

## Golden Vectors
Golden vectors live under `tests/vectors/tlv/` with:
- `manifest.txt` describing schema_id, version, vector, expected summary, and hash
- `*.tlv` vector files (canonical bytes)
- `*.expected.txt` summary output for contract tests
- `*.sha256` hashes of the canonical bytes

Regenerate vectors with:
```
python tests/vectors/gen_tlv_vectors.py --out tests/vectors/tlv
```

## Contract Tests
Contract tests validate cross-module boundaries:
- Setup installed_state -> launcher reader expectations
- Launcher handshake validator
- Pack manifest resolver determinism and refusal codes
- Selection summary embedding in audit logs
- Job journal parsing and resume step selection

Entry point:
```
dominium_contract_tests <test>
```

## Fuzz Harness
`dominium_tlv_fuzz_tests` performs deterministic fuzzing of TLV readers:
- mutated golden vectors (truncation and length errors)
- random byte buffers with bounded size

The fuzz harness must never crash and must return non-OK `err_t` on malformed inputs.

## Updating Schemas Safely
- Add new tags as optional first.
- When a breaking change is required, bump the schema version and add a migration.
- Update golden vectors and ensure contract tests remain green.
