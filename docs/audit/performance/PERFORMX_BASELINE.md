Status: DERIVED
Last Reviewed: 2026-02-11
Supersedes: none
Superseded By: none

# PerformX Baseline Protocol

Baseline updates are explicit and never automatic.

## Update Contract

1. Run `python tools/performx/performx.py run --repo-root .`.
2. Ensure RepoX is green.
3. Update baseline with:
   - `python tools/performx/performx.py baseline --repo-root . --update --justification docs/audit/performance/PERFORMX_BASELINE.md`
4. Commit baseline delta and justification together.

## Guardrails

- Baselines are canonical artifacts and hash-checked.
- Baseline updates require an explanation artifact.
- Hardware run metadata is never copied into canonical baseline payloads.

