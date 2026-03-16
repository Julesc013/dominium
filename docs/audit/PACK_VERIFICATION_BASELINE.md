Status: DERIVED
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Derived From:
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

- `docs/packs/PACK_VERIFICATION_PIPELINE.md`
- `docs/packs/PACK_COMPATIBILITY_MANIFEST.md`

# PACK-COMPAT-1 Baseline

## Verification Summary
- Setup and Launcher now run the same offline verification pipeline before pack activation.
- The pipeline scans portable `dist/packs`, validates `pack.json` plus `pack.compat.json`, checks contract ranges against the pinned/default universe contract bundle, verifies registry requirements, applies MOD-POLICY gates, and dry-runs GEO-9 overlay conflicts.
- Valid pack sets produce a deterministic `pack_lock` artifact and a deterministic `PackCompatibilityReport`.

## Refusal Matrix
- `refusal.pack.schema_invalid`
- `refusal.pack.contract_range_mismatch`
- `refusal.pack.registry_missing`
- `refusal.pack.trust_denied`
- `refusal.pack.conflict_in_strict`

## Pack Lock Rules
- Pack lock ordering is canonical by `(pack_id, pack_version)`.
- Pack lock identity includes:
  - pack ids and versions
  - canonical pack hashes
  - compatibility manifest hashes
  - selected mod policy id
- Hashing is canonical and reproducible across platforms.

## Offline Integration
- Setup commands:
  - `setup verify`
  - `setup list-packs`
  - `setup build-lock`
  - `setup diagnose-pack <pack_id>`
- Launcher commands:
  - verification on `launcher run`
  - `launcher compat-status`

## Readiness
This baseline prepares:
- PACK-COMPAT-2 migration/read-only fallback work
- portable Setup/Launcher verification flows
- future APPSHELL orchestration without repo/XStack dependence at runtime
