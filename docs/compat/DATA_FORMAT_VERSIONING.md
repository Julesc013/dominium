Status: CANONICAL
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/contracts/SEMANTIC_CONTRACT_MODEL.md`, `docs/meta/UNIVERSE_CONTRACT_BUNDLE.md`, and `docs/packs/PACK_VERIFICATION_PIPELINE.md`.

# Data Format Versioning

## Purpose
Define deterministic format versioning, migration, and read-only fallback behavior for persistent Dominium artifacts.

## Artifact Categories
- Save files (`universe_state.json` / save snapshot payloads)
- Blueprint files
- Profile bundles
- Session templates
- Pack lock files

## Required Metadata
Every current-format persistent artifact must declare:
- `format_version`
- `engine_version_created`
- `deterministic_fingerprint`

Universe-bound artifacts must additionally declare:
- `semantic_contract_bundle_hash`

Artifacts may additionally declare:
- `required_contract_ranges`

## Versioning Rules
- `schema_version` continues to version structure.
- `format_version` versions persistent artifact interpretation and migration eligibility.
- Missing `format_version` is treated as legacy `1.0.0` only through the explicit compatibility loader.
- Current MVP baseline format version is `2.0.0` for versioned persistent artifacts introduced by this constitution.

## Migration Rules
- If artifact `format_version` equals current:
  - load normally after schema and metadata validation
- If artifact `format_version` is older than current:
  - attempt deterministic migration path by resolving an explicit migration chain from `data/registries/migration_registry.json`
  - apply each deterministic transform in order
  - log migration events
  - recompute deterministic fingerprint after migration
- If artifact `format_version` is newer than current:
  - attempt read-only mode only when the artifact is safe for observation and semantic contract pins are compatible
  - otherwise refuse with remediation

## Read-Only Fallback
Read-only fallback is permitted only when:
- the artifact is being opened for observation rather than mutation
- semantic contract bundle pins are compatible or absent
- the caller binds `LawProfile` to observation-only behavior

Read-only fallback must:
- emit `explain.read_only_mode`
- record the selected read-only law profile
- forbid mutation paths for that artifact/session

## Refusal Codes
- `refusal.artifact.format_missing`
- `refusal.artifact.format_mismatch`
- `refusal.artifact.migration_missing`
- `refusal.artifact.migration_refused`
- `refusal.artifact.read_only_unavailable`

## Determinism Rules
- Artifact migration order is stable and version-driven.
- Migration chains are selected by ascending `from_version -> to_version`.
- All migration events are canonically serialized and hashed.
- Read-only fallback selection is explicit and logged.
- No silent fallback to reinterpretation.
- No silent reinterpretation is permitted.
