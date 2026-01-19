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
- Canonical formats and migrations defined here live under `schema/`.

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
# SPEC_CORE_DATA_VALIDATION — Core Data Validation Contract

Status: draft  
Version: 1

## Scope
Defines the authoritative validation rules for `/data/core` authoring inputs and
compiled coredata TLV packs. Validation is refusal-first and CI-grade.

## Validation modes
1) **Authoring mode (TOML/JSON)**  
   - Validate raw `/data/core/**` files.  
   - Enforce schema, references, ranges, and policy.

2) **Compiled-pack mode (TLV)**  
   - Validate `pack.tlv` output produced by `coredata_compile`.  
   - Enforce record presence, ordering, hashing, and schema compatibility.

Exactly one mode is used per run.

## Error taxonomy
Each issue MUST include a class and severity.

Classes:
- `SCHEMA_ERROR`: structural violations (missing fields, unknown fields, invalid formats).
- `REFERENCE_ERROR`: unresolved references (missing profiles, invalid cross-links).
- `DETERMINISM_ERROR`: ordering or hashing instability.
- `POLICY_ERROR`: governance rules (e.g., forbidden bindings, neutral profiles).
- `RANGE_ERROR`: values out of allowed bounds.
- `MIGRATION_ERROR`: unsupported schema version without a migration path.

Severity:
- `ERROR`: must refuse (nonzero exit).
- `WARNING`: allowed only for non-sim metadata.

## Exit codes
Exit codes are deterministic and map to the *highest-priority* error class
observed (highest priority listed first):
1) `SCHEMA_ERROR`  -> exit `10`
2) `REFERENCE_ERROR` -> exit `11`
3) `DETERMINISM_ERROR` -> exit `12`
4) `POLICY_ERROR` -> exit `13`
5) `RANGE_ERROR` -> exit `14`
6) `MIGRATION_ERROR` -> exit `15`

Other exit codes:
- `0`: success (no errors)
- `2`: CLI usage / invalid arguments
- `3`: I/O failure (could not read input)

## Determinism rules
- Validation MUST be deterministic across platforms and runs.
- Output ordering MUST be canonical (sorted by stable identifiers).
- Hashes MUST use the canonical hash function specified in core specs.

## Related specs
- `docs/SPEC_CORE_DATA.md`
- `docs/SPEC_COSMO_CORE_DATA.md`
- `docs/SPEC_MECHANICS_PROFILES.md`
- `docs/SPEC_CORE_DATA_PIPELINE.md`
