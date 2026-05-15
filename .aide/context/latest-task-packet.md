# AIDE Latest Task Packet

## PHASE

UNSPECIFIED - DOM-AIDE-02 - Wrap Existing Validators Through AIDE Commands

## GOAL

DOM-AIDE-02 - Wrap Existing Validators Through AIDE Commands

## WHY

Continue AIDE token survival by using repo-local context refs, compact objectives, deterministic validation, and evidence packets instead of long chat history.

## CONTEXT_REFS

- `.aide/memory/project-state.md`
- `.aide/memory/decisions.md`
- `.aide/memory/open-risks.md`
- `.aide/context/dominium-doctrine-refs.md`
- `.aide/context/repo-snapshot.json` (present)
- `.aide/context/repo-map.json` (present)
- `.aide/context/repo-map.md` (present)
- `.aide/context/test-map.json` (present)
- `.aide/context/context-index.json` (present)
- `.aide/context/latest-context-packet.md` (present)
- `.aide/repo/latest-repo-intelligence.md` (present)
- `.aide/tools/latest-tool-inventory.json` (present)
- `.aide/tools/latest-tool-classification.json` (present)
- `.aide/tools/latest-tool-wrap-plan.json` (present)
- `.aide/tools/xstack-wrapper-registry.json` (present)
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

- `.aide/context/**`
- `.aide/reports/DOM-AIDE-02-*`
- `.aide/tools/wrapper-contracts/**`
- `.aide/tools/wrapper-plans/**`
- `.aide/tools/latest-tool-classification.*`
- `.aide/tools/latest-tool-wrap-plan.*`
- `.aide/tools/latest-tool-adapter-map.*`
- `.aide/tools/xstack-wrapper-registry.*`

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

- No Gateway, provider calls, live model routing, local model setup, exact tokenizer, provider billing ledger, Runtime, Service, Commander, Mobile, MCP/A2A, UI, host/app implementation, autonomous loop, product/source/doctrine/tool-root edits, root moves, tool renames, legacy tool execution, build, package, release, full CTest, full FAST, or full eval.

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
- chars: 4182
- approx_tokens: 1046
- budget_status: PASS
- warnings:
  - none
- formal ledger: `.aide/reports/token-ledger.jsonl`

## DOM-AIDE-02 TASK DETAIL

Task: `DOM-AIDE-02 - Wrap Existing Validators Through AIDE Commands`

Immediate goal: create provisional AIDE wrapper contracts and wrapper-plan
evidence for the first low-risk existing validator/check family without
renaming, deleting, moving, or executing legacy tools.

Selected validator family:

- `aide_tool_wrapper_plan_validator`
- selected command: `py -3 .aide/scripts/aide_lite.py tools validate`
- supporting evidence commands: `tools classify`, `tools wrap-plan`

Acceptance:

- Create DOM-AIDE-02 wrapper contract, wrapper plan, selection report,
  validation report, and blocker report under `.aide/**`.
- Keep `execution_allowed = false`, `apply_allowed = false`, network disabled,
  writes disabled for the provisional wrapper contract, and unknown tool
  execution disabled.
- Preserve XStack/AuditX/RepoX/TestX, BuildX-like surfaces, and all existing
  validators.
- Do not modify product/source/doctrine/tool roots.
- Run AIDE validation, `git diff --check`, and scoped status checks.
