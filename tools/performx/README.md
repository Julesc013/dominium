Status: CANONICAL
Last Reviewed: 2026-02-11
Supersedes: none
Superseded By: none

# PerformX

PerformX is the deterministic performance envelope toolchain.

## Commands

- `python tools/performx/performx.py run --repo-root .`
- `python tools/performx/performx.py run --repo-root . --envelope envelope.engine.sim_step_basic`
- `python tools/performx/performx.py baseline --repo-root . --update --justification docs/audit/performance/PERFORMX_BASELINE.md`

## Outputs

- Canonical:
  - `docs/audit/performance/PERFORMX_RESULTS.json`
  - `docs/audit/performance/PERFORMX_REGRESSIONS.json`
- Run metadata:
  - `docs/audit/performance/RUN_META.json`
- Explicit baseline:
  - `docs/audit/performance/PERFORMX_BASELINE.json`

## Determinism Contract

- Canonical artifacts are hash-stable for identical inputs.
- Run metadata may vary and is excluded from determinism checks.
- Regression checks compare normalized metrics and envelope tolerances.

