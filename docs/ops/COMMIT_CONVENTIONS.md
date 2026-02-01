Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Commit Conventions (DEV-OPS-0)

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
