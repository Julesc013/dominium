# AIDE Latest Task Packet

## PHASE

AIDE-MOVE-02-PLAN - second low-risk move planning

## GOAL

Select the next low-risk move candidate from AIDE root recycling evidence, or record that no safe candidate is available. This is no-apply planning evidence only.

## WHY

AIDE-MOVE-01 proved one small docs move. The second wave should not force active tooling, source, or machine-readable metadata into a move plan just to keep moving.

## CONTEXT_REFS

- `.aide/reports/AIDE-GATE-03-post-move-readiness.md`
- `.aide/reports/AIDE-GATE-03-post-move-readiness.json`
- `.aide/reports/AIDE-MOVE-01-APPLY-evidence.json`
- `.aide/reports/roots/AIDE-ROOT-06-reconciliation.json`
- `.aide/reports/roots/AIDE-ROOT-06-move-wave-candidates.json`
- `.aide/reports/roots/ide.inventory.json`
- `.aide/reports/roots/performance.inventory.json`
- `.aide/reports/roots/validation.inventory.json`
- `.aide/reports/roots/governance.inventory.json`
- `.aide/reports/roots/meta.inventory.json`

## ALLOWED_PATHS

- `.aide/refactors/**`
- `.aide/reports/**`
- `.aide/context/**`
- `.aide/ledgers/**`
- `docs/repo/root-recycling/**`

## FORBIDDEN_PATHS

- `apps/**`
- `engine/**`
- `game/**`
- `runtime/**`
- `content/**`
- `tests/**`
- `cmake/**`
- `release/**`
- candidate source files
- ide manifests subtree
- product/version root files
- any file move, delete, rename, or reference rewrite
- path alias activation, salvage application, move-map application, or exception retirement

## IMPLEMENTATION

- Inspect AIDE-GATE-03, AIDE-MOVE-01, AIDE-ROOT-06, and candidate root evidence.
- Select a safe second candidate only if evidence supports it.
- If no safe candidate exists, record a blocked no-candidate plan with refinement next steps.
- Run required AIDE, strict validator, supplemental, plan parsing, and git checks.
- Do not modify candidate source files, manifests, product/source/runtime/build files, maps, aliases, shims, or exception ledgers.

## VALIDATION

Run AIDE, strict validators, supplemental docs/build/UI/ABI checks, plan parsing, and git diff checks. Record results in `.aide/reports/AIDE-MOVE-02-PLAN-validation.md`.

## EVIDENCE

- `.aide/refactors/AIDE-MOVE-02.plan.toml`
- `.aide/refactors/AIDE-MOVE-02.plan.json`
- `.aide/refactors/AIDE-MOVE-02.reference_rewrite_plan.json`
- `.aide/refactors/AIDE-MOVE-02.validation_plan.json`
- `.aide/refactors/AIDE-MOVE-02.rollback_plan.json`
- `.aide/refactors/AIDE-MOVE-02.exception_update_plan.json`
- `.aide/reports/AIDE-MOVE-02-PLAN-status.md`
- `.aide/reports/AIDE-MOVE-02-PLAN-validation.md`
- `.aide/reports/AIDE-MOVE-02-PLAN-blockers.md`
- `.aide/reports/AIDE-MOVE-02-PLAN-review.md`
- `.aide/reports/AIDE-MOVE-02-PLAN-summary.json`
- `docs/repo/root-recycling/AIDE_MOVE_02_SECOND_LOW_RISK_MOVE_PLAN.md`

## NON_GOALS

- Do not apply another move.
- Do not delete files.
- Do not approve or apply move maps or salvage maps.
- Do not create active aliases or compatibility shims.
- Do not retire exceptions.
- Do not change product/source/runtime/build behavior.

## ACCEPTANCE

- Draft plan and support JSON/Markdown exist.
- Candidate selection is evidence-backed.
- If no candidate is selected, blockers and refinement path are explicit.
- Validation passes or only non-blocking known warnings remain.
- No move, delete, rename, reference rewrite, alias, shim, map apply, or exception retirement occurred.

## OUTPUT_SCHEMA

Move-plan outputs are TOML/JSON under `.aide/refactors/**`, Markdown/JSON reports under `.aide/reports/**`, and a narrow repo doc under `docs/repo/root-recycling/**`.

## TOKEN_ESTIMATE

Approximate task packet tokens: 760. No raw source bodies are embedded beyond short path references.
