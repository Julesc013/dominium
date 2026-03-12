Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Commit Conventions (DEV-OPS-0)

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Scope: commit message format used by RepoX changelog automation.

Format
<scope>: <summary>

Rules
- scope is lowercase and one of:
  - engine, game, client, server, tools, launcher, setup
  - docs, schema, data, tests, ci, repox, build, ops, dev
- summary is short, imperative, and ASCII.
- No trailing period.
- No emojis.

Examples
- engine: enforce deterministic ordering in scheduler
- docs: add IDE setup and build matrix
- repox: generate changelog feed from commits
- tools: add ui_ir accessibility validator

Notes
- RepoX groups changelog entries by scope.
- Commits without a valid scope are listed under "uncategorized".
