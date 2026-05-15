# AIDE Latest Task Packet

## PHASE

AIDE-MOVE-01-PLAN - first low-risk root move planning

## GOAL

Create a concrete no-apply move plan for the first low-risk root recycling wave.

## WHY

AIDE-GATE-01 authorized move planning only. The next step is a reviewable plan with exact source and target paths, reference rewrites, validation, rollback, and exception-update expectations before any apply task can be considered.

## CONTEXT_REFS

- `.aide/reports/AIDE-GATE-01-root-move-planning-readiness.md`
- `.aide/reports/roots/AIDE-ROOT-06-first-move-recommendation.md`
- `.aide/reports/roots/AIDE-ROOT-06-move-wave-candidates.md`
- `.aide/refactors/draft_move_wave_AIDE-MOVE-01.json`
- `.aide/refactors/AIDE-MOVE-01.plan.json`
- `docs/repo/root-recycling/AIDE_MOVE_01_FIRST_LOW_RISK_MOVE_PLAN.md`

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
- `ide/**`
- product/version root files
- root move, delete, rename, reference rewrite, path alias activation, salvage application, move-map application, or exception retirement

## IMPLEMENTATION

- Select `ide/README.md` as a draft plan only.
- Defer `ide/manifests/**`.
- Do not modify source root files.
- Do not apply references, maps, shims, aliases, or exceptions.

## VALIDATION

Run AIDE, plan parse, strict validators, supplemental docs/build/UI/ABI checks, and git diff checks. Record results in `.aide/reports/AIDE-MOVE-01-PLAN-validation.md`.

## EVIDENCE

- `.aide/refactors/AIDE-MOVE-01.plan.toml`
- `.aide/refactors/AIDE-MOVE-01.plan.json`
- `.aide/refactors/AIDE-MOVE-01.reference_rewrite_plan.json`
- `.aide/refactors/AIDE-MOVE-01.validation_plan.json`
- `.aide/refactors/AIDE-MOVE-01.rollback_plan.json`
- `.aide/refactors/AIDE-MOVE-01.exception_update_plan.json`
- `.aide/reports/AIDE-MOVE-01-PLAN-review.md`

## NON_GOALS

- Do not move, delete, rename, or rewrite files.
- Do not approve or apply move maps or salvage maps.
- Do not create active aliases or compatibility shims.
- Do not change product/source/runtime/build behavior.
- Do not start AIDE-GATE-02 or an apply task.

## ACCEPTANCE

- Plan artifacts are parseable.
- All plans remain draft, not-approved, and no-apply.
- Exactly one planned move is selected.
- Required reference rewrites, validation, rollback, and exception-update plans exist.
- Validation passes or only known no-apply warnings remain.

## OUTPUT_SCHEMA

Expected artifacts are Markdown, JSON, and TOML planning evidence under the allowed paths. Machine-readable files must include `status`, `approval_status`, and `apply_allowed` fields where applicable.

## TOKEN_ESTIMATE

Approximate task packet tokens: 650. No raw source bodies are embedded beyond short path references.
