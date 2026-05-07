# AIDE Verification Report

## VERIFIER_RESULT

- result: WARN
- method: deterministic repo-local checks
- contents_inline: false
- provider_or_model_calls: none

## CHECK_COUNTS

- info: 111
- warnings: 5
- errors: 0
- checked_files: 62
- changed_files: 23

## CHANGED_FILES

- allowed: `.aide/context/ignore.yaml` (M; matches active task allowed path)
- allowed: `.aide/context/priority.yaml` (M; matches active task allowed path)
- allowed: `.aide/scripts/aide_lite.py` (M; matches active task allowed path)
- allowed: `AGENTS.md` (M; matches active task allowed path)
- unknown: `data/audit/validation_report_FAST.json` (M; does not match active task allowed paths)
- unknown: `docs/audit/VALIDATION_REPORT_FAST.md` (M; does not match active task allowed paths)
- unknown: `.aide.local.example` (??; does not match active task allowed paths)
- unknown: `.aide/cache/latest-cache-keys.json` (??; does not match active task allowed paths)
- unknown: `.aide/cache/latest-cache-keys.md` (??; does not match active task allowed paths)
- allowed: `.aide/context/context-index.json` (??; matches active task allowed path)
- allowed: `.aide/context/dominium-doctrine-refs.md` (??; matches active task allowed path)
- allowed: `.aide/context/latest-context-packet.md` (??; matches active task allowed path)
- allowed: `.aide/context/latest-review-packet.md` (??; matches active task allowed path)
- allowed: `.aide/context/latest-task-packet.md` (??; matches active task allowed path)
- allowed: `.aide/context/repo-map.json` (??; matches active task allowed path)
- allowed: `.aide/context/repo-map.md` (??; matches active task allowed path)
- allowed: `.aide/context/repo-snapshot.json` (??; matches active task allowed path)
- allowed: `.aide/context/test-map.json` (??; matches active task allowed path)
- allowed: `.aide/evals/runs` (??; matches active task allowed path)
- allowed: `.aide/reports` (??; matches active task allowed path)
- allowed: `.aide/routing/latest-route-decision.json` (??; matches active task allowed path)
- allowed: `.aide/routing/latest-route-decision.md` (??; matches active task allowed path)
- allowed: `.aide/verification/latest-verification-report.md` (??; matches active task allowed path)

## WARNINGS

- diff_scope: does not match active task allowed paths `data/audit/validation_report_FAST.json`
- diff_scope: does not match active task allowed paths `docs/audit/VALIDATION_REPORT_FAST.md`
- diff_scope: does not match active task allowed paths `.aide.local.example`
- diff_scope: does not match active task allowed paths `.aide/cache/latest-cache-keys.json`
- diff_scope: does not match active task allowed paths `.aide/cache/latest-cache-keys.md`

## ERRORS

- none

## EVIDENCE_REFS

- `.aide.local.example/README.md`
- `.aide.local.example/cache/README.md`
- `.aide.local.example/config.example.yaml`
- `.aide.local.example/ledgers/README.md`
- `.aide.local.example/traces/README.md`
- `.aide/cache/README.md`
- `.aide/cache/key-policy.yaml`
- `.aide/cache/latest-cache-keys.json`
- `.aide/cache/latest-cache-keys.md`
- `.aide/context/compiler.yaml`
- `.aide/context/context-index.json`
- `.aide/context/excerpt-policy.yaml`
- `.aide/context/ignore.yaml`
- `.aide/context/latest-context-packet.md`
- `.aide/context/latest-task-packet.md`
- `.aide/context/priority.yaml`
- `.aide/context/repo-map.json`
- `.aide/context/repo-map.md`
- `.aide/context/test-map.json`
- `.aide/gateway`
- `.aide/gateway/README.md`
- `.aide/gateway/architecture.md`
- `.aide/gateway/endpoints.yaml`
- `.aide/gateway/lifecycle.yaml`
- `.aide/gateway/security-boundary.md`
- `.aide/memory/decisions.md`
- `.aide/memory/open-risks.md`
- `.aide/memory/project-state.md`
- `.aide/models/capabilities.yaml`
- `.aide/models/fallback.yaml`
- `.aide/models/hard-floors.yaml`
- `.aide/models/providers.yaml`
- `.aide/models/routes.yaml`
- `.aide/policies/cache.yaml`
- `.aide/policies/controller.yaml`
- `.aide/policies/gateway.yaml`
- `.aide/policies/local-state.yaml`
- `.aide/policies/provider-adapters.yaml`
- `.aide/policies/routing.yaml`
- `.aide/policies/token-budget.yaml`
- `.aide/policies/verification.yaml`
- `.aide/prompts/codex-token-mode.md`
- `.aide/prompts/compact-task.md`
- `.aide/prompts/evidence-review.md`
- `.aide/providers`
- `.aide/providers/adapter-contract.yaml`
- `.aide/providers/capability-matrix.yaml`
- `.aide/providers/provider-catalog.yaml`
- `.aide/routing/README.md`
- `.aide/routing/latest-route-decision.json`
- `.aide/routing/latest-route-decision.md`
- `.aide/routing/route-decision.schema.json`
- `.aide/scripts/aide_lite.py`
- `.aide/verification/diff-scope-policy.yaml`
- `.aide/verification/evidence-packet.template.md`
- `.aide/verification/file-reference-policy.yaml`
- `.aide/verification/review-decision-policy.yaml`
- `.aide/verification/review-packet.template.md`
- `.aide/verification/secret-scan-policy.yaml`
- `.gitignore`
- `AGENTS.md`
- `README.md`

## LIMITS

- Structural verifier only; no LLM judging.
- Diff scope is path-based only.
- Secret scan is heuristic only.
- Token counts use chars / 4 approximation.
