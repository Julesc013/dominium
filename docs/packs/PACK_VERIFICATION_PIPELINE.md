Status: CANONICAL
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/packs/PACK_COMPATIBILITY_MANIFEST.md`, `docs/contracts/SEMANTIC_CONTRACT_MODEL.md`, and `docs/modding/MOD_TRUST_AND_CAPABILITIES.md`.

# Offline Pack Verification Pipeline

## Purpose
Define the deterministic offline verification pipeline used by Setup and Launcher before install, upgrade, enable/disable, or session start.

## Verification Steps
1. Enumerate packs in `dist/packs`, sorted by `(pack_id, pack_version)`.
2. Parse adjacent `pack.json` and `pack.compat.json`.
3. Validate:
   - schema correctness
   - trust level allowed by the selected mod policy
   - declared capabilities allowed by the selected mod policy
   - required semantic contract ranges against the active engine/universe contract bundle
   - required registries present in the portable registry set
4. Build dependency graph from declared pack dependencies.
5. Dry-run overlay merge conflict detection using COMPAT-SEM-3 conflict policy.
6. Produce a deterministic `PackCompatibilityReport`.
7. Generate a deterministic `pack_lock.json` when the report is valid.

## Failure Modes
- `refusal.pack.schema_invalid`
- `refusal.pack.contract_range_mismatch`
- `refusal.pack.registry_missing`
- `refusal.pack.trust_denied`
- `refusal.pack.conflict_in_strict`

## Determinism Rules
- Pack order is canonicalized by `(pack_id, pack_version)`.
- Dependency resolution is deterministic and explicit.
- Overlay conflict enumeration is sorted by `(object_id, property_path, layer_order, patch_hash)`.
- All report and lock artifacts use canonical JSON serialization.

## Strict vs Best-Effort
- Strict mode:
  - refuses packs missing `pack.compat.json`
  - refuses dry-run overlay conflicts when conflict policy is strict
  - refuses contract and registry mismatches
- Best-effort mode:
  - may warn on missing optional compatibility surfaces where policy allows
  - still records all disabled or refused surfaces explicitly

## Portable Dist Requirement
Portable `dist/` output must include the schema and registry assets required by offline validation:
- `schemas/`
- `tools/xstack/compatx/version_registry.json`
- `data/registries/`

## Outputs
- `pack_compatibility_report`
- `pack_lock`
- deterministic refusal/explain rows for invalid pack sets
