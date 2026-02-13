Status: DERIVED
Last Reviewed: 2026-02-13
Supersedes: none
Superseded By: none

# Final Performance Validation

## Commands Executed

- `python scripts/dev/gate.py verify --profile-report`
- `python scripts/dev/gate.py strict --profile-report` (cold + warm)
- `python scripts/dev/gate.py full --profile-report`

## Results

- `verify`: PASS (`exit_code=0`), cache hit ratio 1.0, runtime ~0.003s.
- `strict`: PASS (`exit_code=0`), warm runtime ~0.044s, cold runtime remains RepoX-bound.
- `full`: PASS (`exit_code=0`), runtime ~122s with sharded impacted groups.

## Determinism / Safety Checks

- Plan generation remains deterministic (stable hash per stable repo state).
- Cache correctness invariants pass (exact key match required, no false success fallback).
- All lanes preserve canonical gating and do not bypass RepoX/TestX/AuditX contracts.

## Notes

- Cold STRICT remains dominated by full RepoX evaluation.
- Warm verify/strict throughput target is exceeded by large margin due content-addressed cache reuse.
