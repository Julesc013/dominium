Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Release Pipeline (DEV-OPS-0)

Scope: release artifact generation, tagging, and distribution.

Principles
- No release without passing RepoX + TestX.
- No release without deterministic metadata stamping.
- No silent updates.

Pipeline stages (canonical order)
1) Preflight
   - clean working tree
   - allowed branch per release policy
   - required capabilities available
2) Build
   - build all required targets
   - warnings as errors (per policy)
3) Test
   - TestX full suite
   - RepoX full rule set
4) Package
   - build artifacts + packs
   - generate artifact identity manifest
5) Tag
   - create release tag
6) Publish
   - update feeds
   - publish bundles
7) Verify
   - validate update feeds
   - smoke run in clean environment

Tools
- RepoX release command orchestrates all steps (see docs/architecture/BUILD_IDENTITY_MODEL.md).

Release identity, build kinds, and global build numbers
are governed by BUILD_IDENTITY_MODEL.md.

Rollback
- See docs/ops/UPDATE_AND_ROLLBACK.md
