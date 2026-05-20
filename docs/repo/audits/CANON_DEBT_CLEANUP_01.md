Status: DERIVED
Last Reviewed: 2026-05-20
Supersedes: none
Superseded By: none

# CANON-DEBT-CLEANUP-01

Status: PARTIAL PASS
Date: 2026-05-19

## Summary

This cleanup closed the two highest-confidence structural issues that were safe
to merge immediately:

- Archived generated/export AIDE payloads out of active `.aide/`.
- Moved runtime and game public headers out of `engine/include`.
- Moved authored pack payloads out of `contracts/package/packs` into
  `content/packs`.

The remaining items are still real debt, but they require wider reference
repair and should be handled as separate focused changes.

## Completed

### AIDE Authority

Active `.aide/` no longer owns expanded export payloads, generated adapters,
release dist output, or queue evidence payloads. Retained generated AIDE
material is under `archive/generated/aide/`.

### Engine Header Boundary

Runtime-facing headers moved to `runtime/include/`.
World/domain headers moved to `game/include/`.
`domino_engine` still exposes only `engine/include` publicly, with private
runtime/game include roots where existing sources still require them.

### Pack Authority

`contracts/package/packs` now contains only a README guard. Authored pack files
and pack-local manifests moved to `content/packs/<pack_id>/`.

## Validation Run

- PASS: `py -3 .aide/scripts/aide_lite.py doctor`
- PASS_WITH_WARNINGS: `py -3 .aide/scripts/aide_lite.py validate`
- PASS: `python scripts/verify_build_target_boundaries.py`
- PASS: `python scripts/verify_includes_sanity.py`
- PASS: `python scripts/verify_docs_sanity.py --repo-root .`
- PASS: `cmake --preset verify`
- PASS: `cmake --build --preset verify --target ALL_BUILD`
- PASS: `git diff --check`
- PASS: `git diff --cached --check`

Known warning class: AIDE context hash/review-ref drift remains advisory and is
not a merge blocker.

## Remaining Non-Critical Debt

### RUNTIME-NAME-01

Closed by the follow-up runtime naming pass:

- `runtime/shell/commands` merged into `runtime/shell/command`.
- `runtime/render/soft` moved to `runtime/render/software`.
- `runtime/render/stub` moved to `runtime/render/null`.
- `runtime/render/client/renderers` moved to `runtime/render/backend`.
- `runtime/shell/ui_backends` moved to `runtime/ui/backend`.
- `runtime/capability/capability` moved to `runtime/capability/core`.
- `runtime/ui/core` moved to `runtime/ui/service`.

Active CMake, RepoX, AuditX, shell validators, renderer tests, and command
imports now reference the canonical runtime paths.

### GAME-RULE-01

`game/rule` and `game/rules` still coexist. Collapse `game/rules` into
`game/rule` or `game/domain` only after classifying domain-specific rule
ownership.

### SCHEMA-CANON-01

`contracts/schema` still contains old-root and abbreviation buckets such as
`core`, `control`, `lib`, `net`, `packs`, `tool`, `tools`, `geo`, `chem`, and
`diag`. This needs a schema routing table before moving.

### TOOLS-FOLD-01

`tools/` still has many first-level domain/tool roots. Fold user-facing modules
to `apps/workbench`, validators to `tools/validators`, generators to
`tools/codegen`, release helpers to `tools/release`, and domain utilities to a
single canonical domain-tool plane.

### DOCS-TESTS-CANON-01

`docs/` and `tests/` still mirror historical taxonomy in several places. Defer
until active source boundaries are stable.

## Merge Readiness

These commits are safe to merge to `origin/main` because they:

- preserve file contents for moved source and content files;
- avoid semantic ID mutation;
- pass root boundary and include sanity checks;
- pass CMake configure and verify build;
- leave broader taxonomy folds documented rather than guessed.
