# CORE_DATA_GUIDE — Authoring and Validation

Status: draft  
Version: 1

## Purpose
This guide explains how to author `/data/core` and validate it before compiling
to TLV packs. The authoritative contracts live in:
- `docs/SPEC_CORE_DATA.md`
- `docs/SPEC_COSMO_CORE_DATA.md`
- `docs/SPEC_MECHANICS_PROFILES.md`
- `docs/SPEC_CORE_DATA_VALIDATION.md`

## Workflow
1) Author or update `/data/core/**` (TOML preferred).  
2) Validate authoring inputs:
   - `coredata_validate --input-root=data/core`
3) Compile to a pack:
   - `coredata_compile --input-root=data/core --output-pack-id=base_cosmo`
4) Validate compiled packs (optional but recommended):
   - `coredata_validate --pack=repo/packs/base_cosmo/00000100/pack.tlv`

## Common validation errors
- `SCHEMA_ERROR`:
  - Unknown fields in TOML.
  - Missing required keys (e.g., `mechanics_profile_id`).
  - Non-canonical IDs (not lowercase snake_case).
- `REFERENCE_ERROR`:
  - A referenced mechanics profile does not exist.
- `POLICY_ERROR`:
  - Candidate anchor marked `progression_critical`.
  - `galactic_core_extreme` bound to a non-core anchor.
  - Supernova timer used by a non-massive-star profile.
- `RANGE_ERROR`:
  - Values outside allowed bounds (Q16 range, anchor weights).
- `DETERMINISM_ERROR`:
  - Non-canonical ordering or hash mismatches in compiled packs.

## Notes
- Validation is refusal-first; fix the reported issue rather than relying on
  best-effort defaults.
- Warnings apply only to non-sim metadata (for example, missing manifests).
