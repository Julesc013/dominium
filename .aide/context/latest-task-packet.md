# AIDE Latest Task Packet

## PHASE

POST-RESTRUCTURE-00-FULL-PROOF - Full Post-Restructure Proof

## GOAL

Run full post-restructure proof only if MOVE-BULK-08 authorizes it.

## WHY

Feature work and DOE-00 planning require a proven post-restructure baseline, but the proof must not run past a closure gate that says the repo is not ready.

## CONTEXT_REFS

- `.aide/reports/MOVE-BULK-08-CLOSURE-next-readiness.json`
- `.aide/reports/MOVE-BULK-08-CLOSURE-root-matrix.json`
- `.aide/reports/POST-RESTRUCTURE-00-status.md`
- `docs/repo/audits/POST_RESTRUCTURE_00_FULL_PROOF.md`

## ALLOWED_PATHS

- `.aide/reports/**`
- `.aide/context/**`
- `.aide/ledgers/**`
- `docs/repo/audits/**`
- `docs/repo/root-recycling/**`
- `docs/repo/POST_CONVERGE_NEXT_STEPS.md`
- `docs/repo/MOVE_FAMILY_REGRESSION_REQUIREMENTS.md`
- `docs/release/**` proof docs

## FORBIDDEN_PATHS

Moves, deletes, renames, imports, references, shims, path aliases, feature/domain files, product/runtime behavior, public release artifacts, tags, GitHub releases, packages, and installers.

## IMPLEMENTATION

Stopped before full proof because MOVE-BULK-08 says `ready_for_post_restructure_full_proof = false`. Wrote blocked proof evidence only.

## VALIDATION

Initial git sync/ancestry checks passed. Full proof validation was not run because closure readiness blocked it.

## EVIDENCE

- `.aide/reports/POST-RESTRUCTURE-00-status.md`
- `.aide/reports/POST-RESTRUCTURE-00-blockers.md`
- `.aide/reports/POST-RESTRUCTURE-00-next-readiness.json`
- `docs/repo/POST_RESTRUCTURE_PROOF.md`

## NON_GOALS

No full proof execution, no build/test/product/projection/release proof, no feature work, and no root cleanup apply.

## ACCEPTANCE

- Closure readiness was read.
- Blocked status was recorded.
- No proof commands past the closure gate were run.
- Next remediation is exact.

## OUTPUT_SCHEMA

Evidence is Markdown plus JSON reports under schema prefix `dominium.post_restructure_00.*.v1`.

## TOKEN_ESTIMATE

Compact task packet, under 1,200 tokens.
