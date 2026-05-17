# RESTRUCTURE-REPAIR-00 Blockers

## Root Debt

Twenty-three formerly bad roots still contain tracked files and remain under active exceptions. The strict validators pass because these roots are excepted, but the cleanup is not complete. This debt is not safe to fix without the deferred MOVE-BULK batch gates.

Exact next root remediation: `MOVE-BULK-A-SKIPPED-REFERENCE-REFINEMENT`, followed by explicit Batch B-G gates/apply tasks if authorized.

## Full CTest Blockers

- `slice0_hardcoded_ids`: active source/tool/test surfaces contain hardcoded current domain identifiers.
- `slice1_hardcoded_constants`: active source surfaces contain atmosphere/gravity/oxygen assumptions.
- `const_frozen_contract_hashes`: frozen contract hashes do not match current files.
- `inv_override_policy`: override entries expired in March and April 2026.
- `determinism_replay_hash_invariance`: replay hashes differ for performance profiles.
- AuditX CTest cases time out at 300 seconds in the current full run.

## Policy Decisions Not Made

- No frozen hashes were refreshed.
- No override expiry was extended.
- No replay hashes were accepted.
- No root exception was retired or narrowed.
- No `.aide/reports/file-quality-ledger.json` storage-policy change was made.
- Commit `51257dfdb` was not amended after AIDE commit policy flagged missing Markdown headings and `AIDE-Token-Impact`; this is recorded and followed by a compliant evidence commit.

These are deliberate non-actions because each would require policy or semantic approval beyond safe repair.
