# AIDE Latest Task Packet

## PHASE

MOVE-BULK-01-APPLY-DOCS-ARCHIVE - Apply Docs, Evidence, and Archive-Only Cleanup Batch

## GOAL

Apply only the MOVE-BULK Batch A safe subset authorized by MOVE-BULK-00-GATE.

## WHY

Batch A reduces passive root clutter without touching active code, tools, identity, ABI, product, runtime, build, or feature surfaces.

## CONTEXT_REFS

- `.aide/reports/MOVE-BULK-00-GATE-authorized-batches.json`
- `.aide/refactors/MOVE-BULK-00.batch_A_docs_archive.json`
- `.aide/refactors/MOVE-BULK-00.global_reference_rewrite_map.json`
- `.aide/reports/MOVE-BULK-01-APPLY-*`
- `docs/repo/root-recycling/MOVE_BULK_01_DOCS_ARCHIVE_APPLY_RESULT.md`

## ALLOWED_PATHS

- Batch A safe-subset source and target paths
- `.aide/reports/**`
- `.aide/context/**`
- `.aide/ledgers/**`
- `docs/repo/root-recycling/**`
- `docs/repo/audits/**`
- `docs/repo/POST_CONVERGE_NEXT_STEPS.md`
- `docs/repo/MOVE_FAMILY_REGRESSION_REQUIREMENTS.md`

## FORBIDDEN_PATHS

- Active code, active tools, product/runtime/build files, identity-sensitive files, ABI-sensitive files, imports, compatibility shims, active path aliases, unauthorized maps, and unauthorized layout exceptions.

## IMPLEMENTATION

- Applied 26 safe-subset moves.
- Skipped 283 planned files with active/current exact references.
- Applied 0 reference rewrites.
- Retired or narrowed 0 exceptions.

## VALIDATION

Tier 0 validation, stale-reference scan, and git diff checks are required before commit.

## EVIDENCE

- `.aide/reports/MOVE-BULK-01-APPLY-status.md`
- `.aide/reports/MOVE-BULK-01-APPLY-validation.md`
- `.aide/reports/MOVE-BULK-01-APPLY-blockers.md`
- `.aide/reports/MOVE-BULK-01-APPLY-evidence.json`
- `.aide/reports/MOVE-BULK-01-APPLY-moved-items.md`
- `.aide/reports/MOVE-BULK-01-APPLY-skipped-items.md`
- `.aide/reports/MOVE-BULK-01-APPLY-reference-rewrites.md`
- `.aide/reports/MOVE-BULK-01-APPLY-post-state.md`
- `.aide/reports/MOVE-BULK-01-APPLY-rollback.md`

## NON_GOALS

No broad cleanup, no feature work, no build/product proof, no package/release generation, no CMake build, no full CTest, no import rewrites, no shims, and no exception retirement.

## ACCEPTANCE

- Batch A authorization is present.
- Only safe-subset moves are applied.
- Skipped files are recorded with exact reasons.
- No active code, active tools, imports, shims, aliases, exception retirements, product/runtime/build behavior, identity files, or ABI-sensitive files are changed.
- Tier 0 validation and git diff checks are recorded.

## OUTPUT_SCHEMA

Evidence is Markdown plus `.aide/reports/MOVE-BULK-01-APPLY-evidence.json` using schema `dominium.move_bulk_01.apply_docs_archive.v1`.

## TOKEN_ESTIMATE

Compact task packet, under 1,600 tokens.
