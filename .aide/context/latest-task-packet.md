# AIDE Latest Task Packet

## PHASE

CANON-SPINE-NEW - canonical source-spine cleanup.

## GOAL

Collapse second-level wrapper and duplicate source structures into the canonical
spine: runtime shell, runtime UI/render/platform, thin apps, Workbench modules,
deterministic engine, game domain, singular contracts, specific content roots,
and non-interactive tools.

## WHY

Top-level bad-root cleanup is complete, but the active source tree still carried
second-level wrappers such as app/appshell/appcore/core/gui/ui/tool/data and
singular/plural duplicate roots. CANON-SPINE-NEW makes the active ownership
spine usable before feature work resumes.

## CONTEXT_REFS

- `AGENTS.md`
- `contracts/repo/naming.contract.toml`
- `contracts/repo/bad_root_routing.contract.toml`
- `docs/repo/final_repository_structure.md`
- `docs/repo/root-recycling/CANON_SPINE_NEW_RESULT.md`
- `docs/repo/audits/CANON_SPINE_NEW_SOURCE_SPINE_CLEANUP.md`
- `.aide/reports/CANON-SPINE-NEW-status.md`
- `.aide/reports/CANON-SPINE-NEW-validation.md`
- `.aide/reports/CANON-SPINE-NEW-blockers.md`
- `.aide/reports/CANON-SPINE-NEW-summary.json`

## ALLOWED_PATHS

- active source files whose paths/imports/build references changed because of the spine move
- `apps/**`, `engine/**`, `game/**`, `runtime/**`, `contracts/**`, `content/**`, `docs/**`, `tests/**`, `tools/**`, `scripts/**`, `cmake/**`, `release/**`, `archive/**`
- `.aide/reports/**`, `.aide/context/**`, `.aide/ledgers/**`

## FORBIDDEN_PATHS

- `.aide.local/**`
- `.dominium.local/**`
- root `build/**`, `out/**`, `dist/**`, `artifacts/**`, `tmp/**`, `__pycache__/**`
- public release/tag/upload surfaces

## IMPLEMENTATION

- Use `git mv` for tracked structural moves.
- Preserve file contents and semantic IDs.
- Repair stale paths/imports/build references caused by the move.
- Keep generated/local roots untracked.
- Record evidence and remaining blockers.

## VALIDATION

- AIDE doctor/validate/test/selftest/tools/roots/repo.
- Strict repo/root/distribution/component validators.
- Bad-root absence and naming validators.
- Docs/UI/ABI/include sanity.
- CMake configure.
- Smoke CTest and focused spine CTest.
- Git diff checks.

## EVIDENCE

- `.aide/reports/CANON-SPINE-NEW-status.md`
- `.aide/reports/CANON-SPINE-NEW-validation.md`
- `.aide/reports/CANON-SPINE-NEW-blockers.md`
- `.aide/reports/CANON-SPINE-NEW-summary.json`

## NON_GOALS

- no feature implementation
- no public release/tag/upload
- no deletion of tracked source
- no semantic ID mutation
- no final full-proof claim while boundary/full CTest blockers remain

## ACCEPTANCE

PASS_WITH_WARNINGS is acceptable when AIDE and strict structural validators pass,
former bad roots remain empty, smoke/focused spine tests pass, and remaining
boundary/full-proof blockers are documented.

## OUTPUT_SCHEMA

Evidence is Markdown plus compact JSON under `.aide/reports/CANON-SPINE-NEW-*`.

## TOKEN_ESTIMATE

This packet is intentionally compact and references evidence by path.

## STATUS

PASS_WITH_WARNINGS. Feature work remains blocked. Next task is
`CANON-SPINE-BOUNDARY-01 - Repair Remaining Boundary Imports and Full Proof`.
