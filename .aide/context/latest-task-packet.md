# AIDE Latest Task Packet

## PHASE

RELEASE-00 - Internal Pilot Release 0

## GOAL

Stage and validate a local-only internal pilot release proof tree from the proven portable projection. Preserve generated release bytes under `.dominium.local/` and commit only proof evidence, docs, and narrow local tooling.

## WHY

Dominium needs one self-describing internal proof artifact before moving into operating-environment MVP spine work. RELEASE-00 collects the proven projection, manifests, checksums, proof reports, warning ledger, runbook, and rollback notes without publishing a release.

## CURRENT RESULT

PASS_WITH_WARNINGS. Internal Pilot Release 0 is staged under `.dominium.local/releases/internal-pilot-0`; strict validation passes with no blockers and verifies 4718 checksum entries.

## CONTEXT_REFS

- `docs/repo/audits/RELEASE_00_INTERNAL_PILOT_RELEASE.md`
- `docs/release/INTERNAL_PILOT_RELEASE_0.md`
- `docs/release/PORTABLE_PROJECTION_PROOF.md`
- `docs/release/INTERNAL_PILOT_READINESS.md`
- `.aide/reports/RELEASE-00-internal-pilot-results.json`
- `.aide/reports/RELEASE-00-release-tree.json`
- `.aide/reports/RELEASE-00-next-readiness.json`
- `.aide/reports/RELEASE-00-validation.md`
- `.aide/reports/RELEASE-00-blockers.md`

## IMPLEMENTATION

RELEASE-00 adds a narrow local-only stager and read-only validator, stages `.dominium.local/releases/internal-pilot-0`, validates manifests/checksums/proofs/binaries, and records readiness for DOE-00.

## EVIDENCE

- Portable projection input: `.dominium.local/projections/post-converge-12/v0.0.0-post-converge-12/win64/dominium`.
- Internal release root: `.dominium.local/releases/internal-pilot-0`.
- Validator: `python tools/validators/check_internal_pilot_release.py --repo-root . --release-root .dominium.local/releases/internal-pilot-0 --json --strict`.
- Result: PASS, blockers none, checksum entries 4718.

## NON_GOALS

- no root moves, deletes, renames, aliases, move maps, or salvage maps
- no public release, GitHub release, tag, upload, installer, or package publication
- no committed generated release/projection/build output
- no product/runtime/source behavior changes
- no RepoX/AuditX/TestX weakening

## ACCEPTANCE

- portable projection input is read and accepted
- local release staging root is generated under ignored `.dominium.local/`
- internal pilot manifest, provenance, checksums, proof reports, warning ledger, runbook, and rollback notes exist
- strict internal pilot validator passes
- generated release staging remains uncommitted
- exact next task is recommended

## OUTPUT_SCHEMA

Human-readable reports plus JSON evidence:

- `.aide/reports/RELEASE-00-internal-pilot-results.json`
- `.aide/reports/RELEASE-00-release-tree.json`
- `.aide/reports/RELEASE-00-next-readiness.json`

## TOKEN_ESTIMATE

Latest packet is intended to stay below the AIDE compact-context budget.

## ALLOWED_PATHS

- AIDE reports/context/ledger
- post-converge and release status docs
- release audit evidence
- local-only release stager and read-only validator

## FORBIDDEN_PATHS

- product/runtime/source behavior changes
- committed generated product/projection/package/release artifacts
- public release, GitHub release, tag, upload, installer, or package publication
- root moves, deletes, renames, aliases, or move maps
- broad AuditX output regeneration
- RepoX/AuditX/TestX weakening

## VALIDATION

RELEASE-00 validates the stager, read-only validator, release root checksum/provenance/proof structure, JSON reports, AIDE checks, repo/layout/distribution/component validators, docs/build/UI/ABI checks, and git diff hygiene.

## NEXT

Recommended next task: `DOE-00 - Dominium Operating Environment Doctrine and Boot Spine Plan`. Validation-speed follow-up remains `TEST-PERF-01 - CTest Sharding and Slow-Test Baseline`.
