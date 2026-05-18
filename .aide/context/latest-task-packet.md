# AIDE Latest Task Packet

## PHASE

NAME-00 redo - Directory, File, Language, and Ownership Naming Canon

## GOAL

Refresh the NAME-00 naming canon evidence against current `main` after TEST-PERF-01, semantic lint repair, and MOVE-SCRIPT-00. Keep the task no-apply: no file moves, deletes, renames, import rewrites, reference rewrites, shims, move maps, salvage maps, generated outputs, release work, or exception retirement.

## WHY

The repository has a naming canon, but the redo prompt requires current conflict counts, explicit answers to the naming-law questions, and a clear bridge from NAME-00 to MOVE-SCRIPT-00 and `MOVE-BULK-BG-REFINEMENT-00`.

## CONTEXT_REFS

- `AGENTS.md`
- `contracts/repo/layout.contract.toml`
- `contracts/repo/root_allowlist.toml`
- `contracts/repo/layout_exceptions.toml`
- `contracts/repo/naming.contract.toml`
- `docs/repo/directory_naming.md`
- `docs/repo/file_naming.md`
- `docs/repo/no_src_source_policy.md`
- `docs/repo/module_layout.md`
- `docs/repo/language_ownership.md`
- `docs/repo/audits/NAME_00_NAMING_CANON_AUDIT.md`
- `.aide/reports/NAME-00-status.md`
- `.aide/reports/NAME-00-validation.md`
- `.aide/reports/NAME-00-blockers.md`
- `.aide/reports/NAME-00-path-conflicts.json`
- `.aide/reports/NAME-00-language-ownership-findings.json`
- `.aide/reports/MOVE-SCRIPT-00-routing-preview.json`
- `.aide/reports/MOVE-SCRIPT-00-skipped-ledger.json`
- `.aide/reports/MOVE-SCRIPT-00-batch-plan.json`

## ALLOWED_PATHS

- `contracts/repo/naming.contract.toml`
- `docs/repo/**`
- `tools/validators/repo/**`
- `.aide/reports/**`
- `.aide/context/**`
- `.aide/ledgers/**`

## FORBIDDEN_PATHS

- `.dominium.local/**`
- `.aide.local/**`
- generated build/projection/release outputs
- product/runtime/engine/game behavior files
- content/package/profile/bundle identity files unless explicitly required by naming evidence

## IMPLEMENTATION

- Read the current naming contract and root/layout authority first.
- Keep changes inside allowed naming/status/evidence paths.
- Preserve generated/manual boundaries.
- Record current counts from validators and MOVE-SCRIPT-00 evidence.
- Do not inline full raw validator output when summary counts and report paths are enough.

## VALIDATION

- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `py -3 .aide/scripts/aide_lite.py test`
- `py -3 .aide/scripts/aide_lite.py selftest`
- `py -3 .aide/scripts/aide_lite.py tools validate`
- `py -3 .aide/scripts/aide_lite.py roots validate`
- `py -3 .aide/scripts/aide_lite.py repo validate`
- strict repo/root/distribution/component validators
- NAME-00 validators
- Python compile for NAME-00 validators
- JSON parse for touched JSON
- docs/build/UI/ABI supplemental checks
- `git diff --check`

## EVIDENCE

- changed files
- validation commands and results
- current NAME-00 conflict counts
- current MOVE-SCRIPT-00 dry-run counts
- unresolved warnings and deferrals

## ACCEPTANCE

- Naming contract and human docs remain active.
- Current conflict counts are recorded.
- No naming migration is applied.
- Future MOVE-BULK B-G refinement is bound to the naming contract and dry-run router evidence.
- Validation is run and reported honestly.

## NON_GOALS

- No root movement, deletion, rename, reference rewrite, import rewrite, shim, layout exception retirement, feature work, generated output commit, package/release generation, tag, or GitHub release.

## NEXT

`MOVE-BULK-BG-REFINEMENT-00 - Re-Gate Deferred B-G Cleanup`

## OUTPUT_SCHEMA

Return a compact final report with `STATUS`, `SUMMARY`, `COMMITS`, `VALIDATION`, `RISKS`, and `NEXT`.

## TOKEN_ESTIMATE

- method: approximate manual estimate
- approx_tokens: 900
- budget_status: PASS
- warnings:
  - none
