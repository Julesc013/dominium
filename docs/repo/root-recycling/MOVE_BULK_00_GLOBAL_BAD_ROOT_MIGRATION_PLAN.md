Status: DRAFT
Last Reviewed: 2026-05-18
Supersedes: MOVE-FAMILY micro-planning cadence for remaining bad-root cleanup
Superseded By: none

# MOVE-BULK-00 Global Bad-Root Migration Plan

## Status

MOVE-BULK-00 creates a global no-apply migration plan for the remaining tracked noncanonical roots.

- Status: `draft`
- Approval status: `not_approved`
- Apply allowed: `false`
- Baseline: BASELINE-00 / RELEASE-00 structural regression baseline
- Next task: `MOVE-BULK-00-GATE - Global Bad-Root Migration Gate`

## Scope

The plan inspects all remaining tracked files under:

`core/`, `control/`, `data/`, `packs/`, `profiles/`, `bundles/`, `compat/`, `lib/`, `libs/`, `locks/`, `repo/`, `safety/`, `security/`, `specs/`, `updates/`, `meta/`, `governance/`, `performance/`, `validation/`, `modding/`, `models/`, `templates/`, and `net/`.

`ide/` is excluded from remaining work because it was retired by MOVE-FAMILY-00B and `git ls-files ide` is empty.

## Summary

- Remaining bad roots inspected: 23.
- Tracked files under bad roots: 1,790.
- Initial gate-ready file count: 309.
- Deferred until batch gates: 1,481.
- Explicit blocked file count: 1.
- First ready batch: Batch A docs/evidence/archive-only.

## Batch Plan

| Batch | Scope | Files | Gate State |
| --- | --- | ---: | --- |
| A | docs/evidence/archive-only | 309 | ready |
| B | templates/models/modding | 6 | needs owner review |
| C | content identity | 1230 | needs identity validation gate |
| D | authority/policy/spec/update | 50 | needs authority contract gate |
| E | active tools/modules | 33 | needs shim/import gate |
| F | runtime/core/net | 54 | needs runtime/build/product gate |
| G | libraries/ABI | 108 | needs ABI/build gate |
| H | final exception/shim closure | 0 | waits for prior batches |

## Ownership Rules

- Deterministic substrate moves toward `engine/`.
- Domain/game rules move toward `game/`.
- Runtime services and adapters move toward `runtime/`.
- Protocols, capabilities, ABI, schemas, registries, and law move toward `contracts/`.
- Authored packs, profiles, assets, and domain data move toward `content/`.
- Human explanation and current docs move toward `docs/`.
- Tests, fixtures, and golden cases move toward `tests/`.
- Validators, generators, migration helpers, and developer tools move toward `tools/`.
- Small wrappers move toward `scripts/`.
- Third-party material moves toward `external/`.
- Release recipes and update policy move toward `release/`.
- Historical, superseded, quarantined, and retained generated evidence moves toward `archive/`.

## Apply Strategy

Each later apply prompt must apply only a gate-approved safe subset, skip unsafe items with exact blockers, and run batch-specific validation. The global plan does not authorize any apply task.

## Validation Strategy

Tier 0 is required for every batch. Higher-risk batches add RepoX, import smoke, content/pack/profile proof, projection/release proof, CMake/build, focused or smoke CTest, product boot, ABI checks, and final post-restructure proof as needed.

## Rollback Strategy

Every batch has a rollback plan covering reverse moves, reverse imports, reverse references, shim removal, exception restoration, and post-rollback validation.

## No-Apply Confirmation

MOVE-BULK-00-PLAN moved no files, deleted no files, renamed no files, rewrote no imports or references, created no shims, applied no maps, and retired no exceptions.

## MOVE-BULK-00-GATE Result

MOVE-BULK-00-GATE passed with warnings and authorizes only Batch A for the next apply task.

- Authorized next task: `MOVE-BULK-01-APPLY-DOCS-ARCHIVE`.
- Authorized scope: Batch A docs/evidence/archive-only safe subset under `data/`.
- Authorized file count: 309 planned files.
- Deferred batches: B, C, D, E, F, and G.
- Blocked batch: H until prior batches apply and prove cleanly.
- Feature work remains unauthorized.

The gate did not move files, rewrite references, create shims, apply maps, or retire exceptions.
