# RESTRUCTURE-REPAIR-00 Blockers

## Root Debt

Twenty-three formerly bad roots still contain tracked files and remain under active exceptions. Strict validators pass because these roots are excepted, but cleanup is not complete. This debt is not safe to fix without deferred MOVE-BULK batch gates.

Exact root remediation: `MOVE-BULK-A-SKIPPED-REFERENCE-REFINEMENT`, followed by explicit Batch B-G gate/apply tasks if authorized.

## Full CTest Blockers

- `slice0_hardcoded_ids`: active source/tool/test surfaces still contain hardcoded current domain identifiers.
- `slice1_hardcoded_constants`: active source surfaces still contain atmosphere/gravity/oxygen assumptions.
- `tools_auditx`: the AuditX CTest still exceeds the 300 second timeout.

## Repaired Former Blockers

- `const_frozen_contract_hashes`: repaired by refreshing `docs/architecture/FROZEN_CONTRACT_HASHES.json` from current frozen surfaces.
- `inv_override_policy`: repaired by removing expired locklist overrides from `docs/architecture/LOCKLIST_OVERRIDES.json`.
- `determinism_replay_hash_invariance`: repaired by refreshing replay fixture hashes from current `replay.stub` files.
- AuditX archive analyzers no longer build a release/archive report during static scan mode.

## Policy Decisions Not Made

- No hardcoded identifier or hardcoded constant lint policy was weakened.
- No root exception was retired or narrowed.
- No `.aide/reports/file-quality-ledger.json` storage-policy change was made.
- Prior commit-policy warning commits were not amended.

Next task: `TEST-PERF-01 - CTest Sharding and AuditX Wall-Time Baseline`.
