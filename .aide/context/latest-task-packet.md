# AIDE Latest Task Packet

## PHASE

UNSPECIFIED - DOMINIUM-AIDE-COMMIT-FINALIZATION-01 - Commit AIDE Baseline Evidence and Re-run Commit Check

## GOAL

DOMINIUM-AIDE-COMMIT-FINALIZATION-01 - Commit AIDE Baseline Evidence and Re-run Commit Check

## WHY

Continue AIDE token survival by using repo-local context refs, compact objectives, deterministic validation, and evidence packets instead of long chat history.

## CONTEXT_REFS

- `.aide/memory/project-state.md`
- `.aide/memory/decisions.md`
- `.aide/memory/open-risks.md`
- `.aide/context/repo-snapshot.json` (present)
- `.aide/context/repo-map.json` (present)
- `.aide/context/repo-map.md` (present)
- `.aide/context/test-map.json` (present)
- `.aide/context/context-index.json` (present)
- `.aide/context/latest-context-packet.md` (present)
- `.aide/repo/latest-repo-intelligence.md` (present)
- `.aide/repo/file-inventory.json` (present)
- `.aide/reports/file-quality-summary.md` (present)
- `.aide/reports/file-quality-ledger.json` (present)
- `.aide/refactors/latest-refactor-readiness.md` (present)
- `.aide/refactors/latest-refactor-plan.example.json` (present)
- `.aide/routing/latest-route-decision.json` (present)
- `.aide/routing/latest-route-decision.md` (present)
- `.aide/cache/latest-cache-keys.json` (present)
- `.aide/cache/latest-cache-keys.md` (present)
- `.aide/prompts/compact-task.md`
- `.aide/policies/token-budget.yaml`
- `.aide/policies/cache.yaml`
- `.aide/policies/local-state.yaml`

## ALLOWED_PATHS

- `<fill from the next reviewed queue packet>`
- `.aide/context/**`
- `.aide/queue/unspecified-*` if this task becomes a queue item
- root docs only when behavior or documentation links change

## FORBIDDEN_PATHS

- `.git/**`
- `.env`
- `secrets/**`
- `.aide.local/**`
- raw provider credentials, API keys, local caches, raw prompt logs
- Gateway, provider, Runtime, Service, Commander, Mobile, MCP/A2A, host, or app-surface implementation paths unless the queue packet explicitly authorizes them

## IMPLEMENTATION

- Read the queue packet and relevant repo refs first.
- Keep changes inside the allowed paths.
- Make the smallest coherent diff that satisfies acceptance.
- Preserve generated/manual boundaries.
- Do not inline whole source files unless exact contents are required.
- Use exact refs such as `path#Lstart-Lend` when file details are load-bearing.

## VALIDATION

- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py index`
- `py -3 .aide/scripts/aide_lite.py context`
- `py -3 .aide/scripts/aide_lite.py repo inventory`
- `py -3 .aide/scripts/aide_lite.py repo validate`
- `py -3 .aide/scripts/aide_lite.py verify`
- `py -3 .aide/scripts/aide_lite.py review-pack`
- `py -3 .aide/scripts/aide_lite.py route explain`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 scripts/aide validate`
- `git diff --check`

## COMMITS

- Commit coherent subdeliverables with verbose bodies.
- Stop at review gates.

## EVIDENCE

- changed files
- validation commands and results
- verifier result
- review packet path and result when review-pack is available
- advisory route decision path and result when Q17 routing is available
- compact packet size and budget status
- unresolved risks and deferrals

## NON_GOALS

- No Gateway, provider calls, live model routing, local model setup, exact tokenizer, provider billing ledger, Runtime, Service, Commander, Mobile, MCP/A2A, UI, host/app implementation, or autonomous loop unless this packet is superseded by a reviewed queue item that explicitly authorizes it.

## ACCEPTANCE

- Task-specific acceptance criteria are met.
- Validation is run and recorded.
- Evidence is written.
- No secrets, raw prompt logs, local caches, or `.aide.local` contents are committed.

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `COMMITS`, `CHANGED_FILES`, `VALIDATION`, route/verifier/token results, `RISKS`, and `NEXT`.
Include the verifier result when Q12 verifier behavior is available.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- chars: 5579
- approx_tokens: 1395
- budget_status: PASS
- warnings:
  - none
- formal ledger: `.aide/reports/token-ledger.jsonl`

## DOMINIUM DCHECK-01 NEXT TASK DETAIL

Task: `DOMINIUM-AIDE-COMMIT-FINALIZATION-01 - Commit AIDE Baseline Evidence and Re-run Commit Check`

Immediate goal: make the currently usable Dominium AIDE baseline durable. DCHECK-01 found that Q49-Q53 executed and AIDE core validation works, and the audit checkpoint is committed. Q52/Q53/Q53R evidence, generated `.aide/**` outputs, and the Q53R `.aide/scripts/aide_lite.py` repair are still uncommitted.

Required refs:

- `.aide/queue/DCHECK-01-dominium-aide-operating-baseline-audit/audit-report.md`
- `.aide/queue/DCHECK-01-dominium-aide-operating-baseline-audit/readiness-and-next-plan.md`
- `.aide/queue/DOMINIUM-AIDE-BASELINE-REPAIR-01/`
- `.aide/queue/DOMINIUM-AIDE-ROOT-RECYCLING-01/`
- `.aide/queue/DOMINIUM-AIDE-OPERATING-BASELINE-01/`
- `.aide/scripts/aide_lite.py`

Acceptance:

- Stage only AIDE baseline evidence, generated AIDE status outputs, and the Q53R AIDE repair needed to reproduce validation.
- Do not edit product/source/doctrine/tool roots.
- Confirm `.aide.local/` and secrets are not staged.
- Run `doctor`, `validate`, `test`, `selftest`, `verify`, roots/tools/lifecycle validators, `xstack validate`, `git diff --check`, and `commit check --latest`.
- Commit with AIDE Commit Discipline v0.
- After commit finalization, the global path may resume `Q54 Eureka Fresh Upgrade Preflight`.
