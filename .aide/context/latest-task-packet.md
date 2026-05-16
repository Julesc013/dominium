# AIDE Latest Task Packet

## PHASE

AIDE-MOVE-02-REFINE - identify second low-risk candidate

## GOAL

Refine the second move candidate search after AIDE-MOVE-02-PLAN found no safe candidate. This is no-apply refinement evidence only.

## WHY

AIDE should not force a second move wave if the remaining candidates are active tooling, policy-sensitive, authority-sensitive, build-sensitive, or machine-readable metadata.

## CONTEXT_REFS

- `.aide/reports/AIDE-MOVE-02-PLAN-status.md`
- `.aide/reports/AIDE-MOVE-02-PLAN-blockers.md`
- `.aide/reports/AIDE-MOVE-02-PLAN-summary.json`
- `.aide/refactors/AIDE-MOVE-02.plan.json`
- `.aide/reports/roots/ide.inventory.json`
- `.aide/reports/roots/performance.inventory.json`
- `.aide/reports/roots/validation.inventory.json`
- `.aide/reports/roots/governance.inventory.json`
- `.aide/reports/roots/meta.inventory.json`
- `.aide/reports/roots/templates.inventory.json`
- `.aide/reports/roots/templates.classification.json`

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
- product/version root files
- any file move, delete, rename, or reference rewrite
- path alias activation, salvage application, move-map application, or exception retirement

## IMPLEMENTATION

- Re-read AIDE-MOVE-02 blocker evidence and root reports.
- Search for single-file docs-only, README, historical/evidence, or generated review candidates.
- Reject active Python/tooling, machine-readable metadata, identity-sensitive content, authority-sensitive specs, build-sensitive inputs, and template scaffolds with protected references.
- Create candidate/refinement reports and no-candidate JSON if no candidate survives.

## VALIDATION

Run AIDE, strict validators, supplemental docs/build/UI/ABI checks, JSON parsing, and git diff checks. Record results in `.aide/reports/AIDE-MOVE-02-REFINE-validation.md`.

## EVIDENCE

- `.aide/reports/AIDE-MOVE-02-REFINE-status.md`
- `.aide/reports/AIDE-MOVE-02-REFINE-candidates.md`
- `.aide/reports/AIDE-MOVE-02-REFINE-candidates.json`
- `.aide/reports/AIDE-MOVE-02-REFINE-decision.md`
- `.aide/reports/AIDE-MOVE-02-REFINE-validation.md`
- `.aide/reports/AIDE-MOVE-02-REFINE-blockers.md`
- `.aide/refactors/AIDE-MOVE-02.no_candidate.json`
- `docs/repo/root-recycling/AIDE_MOVE_02_REFINEMENT.md`

## NON_GOALS

- Do not move files.
- Do not delete files.
- Do not rename files.
- Do not rewrite references.
- Do not approve or apply move maps or salvage maps.
- Do not create aliases or shims.
- Do not retire exceptions.
- Do not change product/source/runtime/build behavior.

## ACCEPTANCE

- Candidate report and decision report exist.
- No-candidate JSON exists if no safe candidate survives.
- Next task recommendation is explicit.
- Validation passes or only known warnings remain.
- No move/delete/rename/reference rewrite/alias/shim/map application/exception retirement occurred.

## OUTPUT_SCHEMA

Refinement outputs are Markdown and JSON reports under `.aide/reports/**`, a no-candidate JSON artifact under `.aide/refactors/**`, and narrow root-recycling documentation under `docs/repo/root-recycling/**`.

## TOKEN_ESTIMATE

Approximate task packet tokens: 850. No raw source bodies are embedded beyond short path references.
