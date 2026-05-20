Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none

# Restructure Repair Status

Latest task: `MOVE-SCRIPT-00`.

Result: PARTIAL, with naming law locked, CTest sharding honest, semantic lint blockers resolved, and deterministic bad-root routing evidence generated without applying moves.

## PUBLIC-SURFACE-REGISTRY-01 Update

PUBLIC-SURFACE-REGISTRY-01 is PASS_WITH_WARNINGS.

- public surface registry: `contracts/public_surface/public_surface.contract.toml`.
- validator: `python tools/validators/repo/check_public_surface.py --repo-root . --strict`.
- initial registry: 20 surfaces, 25 kinds, 12 stability classes.
- stable entries: 2 repo governance contracts with strict validator proof.
- fast strict: PASS, 30/30 commands, 299.828 seconds.
- feature implementation remains blocked until Foundation Lock closes.

Next task:
`API-ABI-CANON-01`

## FAST-STRICT-TEST-TIER-01 Update

FAST-STRICT-TEST-TIER-01 is PASS_WITH_WARNINGS.

- normal gate: `fast_strict` = T0 + T1 + T2.
- command: `python tools/test/run_fast_strict.py --repo-root .`
- latest result: PASS, 30/30 commands, 332.828 seconds.
- full CTest remains T4 full/release debt and was not rerun for this task.
- feature implementation remains blocked until Foundation Lock closes.

Next task:
`PUBLIC-SURFACE-REGISTRY-01`

## Current Green Gates

- AIDE doctor/validate/test/selftest/tools/roots/repo pass.
- Strict layout/root/distribution/component validators pass.
- Focused RepoX passes.
- Smoke CTest passes.
- Fast CTest label passes.
- Semantic lint CTest lanes pass.
- AuditX slow shard passes.
- Native configure and build-only `ALL_BUILD` pass.
- Product boot, portable projection, and internal pilot release validators pass.
- Frozen contract guard passes.
- Override policy tests pass.
- Replay hash invariance passes.

## Current Blockers

- Full CTest is not green.
- Twenty-three formerly bad roots remain under active exceptions.
- Current dry-run router inventory finds 1,765 tracked files under the former bad roots.
- `tools_auditx` no longer blocks the 300 second fast lane after `TEST-PERF-01`; AuditX is split into explicit `audit`/`auditx`/`slow`/`nightly` CTest shards with a 1200 second timeout.
- The tracked `.aide/reports/file-quality-ledger.json` large-file policy remains unresolved.
- The first two repair evidence commits failed AIDE commit-message policy and were not amended; the follow-up commit records the warnings.
- Existing naming conflicts are classified by NAME-00 but not moved or rewritten.

## Next Task

`MOVE-BULK-BG-REFINEMENT-00 - Re-Gate Deferred B-G Cleanup`

DOE-00 is not ready. Feature implementation remains blocked.

## NAME-00 Update

NAME-00 added `contracts/repo/naming.contract.toml`, human naming docs, warning-oriented naming validators, and conflict evidence under `.aide/reports/NAME-00-*`.

The naming canon does not authorize moves. Future MOVE-BULK B-G refinement must use the NAME-00 target grammar and keep planned internal renames as future work only.

NAME-00 redo at `148a9adf95bb678da16784434221c568f7bb96cb` refreshed the current evidence after MOVE-SCRIPT-00:

- naming-law blockers: 0.
- current bad-root dry-run inventory: 1,765 tracked files.
- route candidates: 1,593.
- skipped/deferred files: 172.
- target collisions: 0.

The redo records current answers to the naming-law prompt but still applies no moves, renames, imports, references, shims, maps, or exception retirements.

## TEST-PERF-01 Update

TEST-PERF-01 measured 495 `verify` CTest tests, 57 smoke tests, 57 fast-label tests, and 3 AuditX slow-shard tests.

Current measured lanes:

- focused RepoX: PASS in 128.978 seconds.
- smoke CTest: PASS in 55.829 seconds.
- fast CTest: PASS in 48.821 seconds.
- AuditX shard: PASS in 824.573 seconds.

Full CTest remains governed by the TEST-PERF-01 sharded execution model.

## SEMANTIC-LINTS Update

POST-RESTRUCTURE-REPAIR-SEMANTIC-LINTS reproduced and classified 1,104 hardcoded identifier/constant findings:

- `preserve_doctrine_constant`: 213.
- `preserve_fixture_literal`: 582.
- `preserve_protocol_literal`: 264.
- `preserve_schema_literal`: 45.

Current semantic lint lanes:

- `slice0_hardcoded_ids`: PASS in 7.93 seconds.
- `slice1_hardcoded_constants`: PASS in 3.00 seconds.
- combined semantic lint rerun: PASS in 11.01 seconds.

The allowlist is exact-match only and lives at `contracts/repo/semantic_lint_allowlist.json`.

## MOVE-SCRIPT-00 Update

MOVE-SCRIPT-00 added a dry-run-only bad-root router under `tools/migration/`.

Current dry-run evidence:

- bad-root tracked files: 1,765.
- move candidates: 1,593.
- skipped/deferred files: 172.
- target collisions: 0.
- moves applied: 0.
- exceptions retired: 0.

The router consumes the NAME-00 target grammar and emits route candidates, skip/defer reasons, per-root summaries, and B-G batch summaries. It refuses ambiguous targets, collisions, identity-sensitive routes without clear ownership, active Python/import-sensitive packages without rewrite or shim plans, authority-sensitive docs-only routes, normative `specs/reality` material, and forbidden target segments such as `source` and generic `compat`.

## MOVE-ROUTER-01 Update

MOVE-ROUTER-01 replaced the skipped/deferred posture with deterministic
quarantine routing and applied the route table with `git mv`.

- bad-root tracked files before: 1,765.
- bad-root tracked files after: 0.
- semantic moves: 1,694.
- quarantine moves: 71.
- skipped moves: 0.
- target collisions: 0.
- active root exceptions retired: 23.

Current blockers shift from root presence to repair proof:

- old bad-root path references remain.
- imports and CMake/build paths may be stale.
- quarantined files require later owner review before promotion.
- full proof remains blocked until `MOVE-ROUTER-02` repairs references/imports/build/projection surfaces.

Next task:
`MOVE-ROUTER-02 - Repair References, Imports, Build, Projection, and Exceptions After Routing`

## MOVE-ROUTER-02 Update

MOVE-ROUTER-02 is PARTIAL.

- Former bad roots remain empty in tracked source.
- Bad-root absence, strict repo layout, and strict root allowlist validators pass.
- CMake configure passes.
- Integrated fast/smoke tests reached by the build pass: 57/57 passing.
- Broader TestX remains red: 140 of 344 lanes failed.

Remaining blocker classes:

- RepoX ruleset discovery still points at old `repo/repox/rulesets`.
- Registry and pack consumers still expect old `data/` and `packs/` paths.
- Some old import package shapes and source path expectations remain.
- Frozen hashes and generated evidence need reviewed disposition.

Next task:
`MOVE-ROUTER-02R - Finish Registry, Ruleset, Import, and Test Path Repair After Routing`

## CANON-SPINE-NEW Update

CANON-SPINE-NEW is PASS_WITH_WARNINGS.

- Former bad roots remain empty in tracked source.
- Runtime shell, workbench, engine/runtime split, game/domain, contracts,
  content, docs, and tools were routed toward the canonical source spine.
- Strict layout/root/distribution/component validators pass.
- AIDE doctor/validate/test/selftest/tools/roots/repo pass.
- Smoke CTest and focused spine CTest pass.
- Remaining blockers are boundary validation and broad full CTest.

Next task:
`CANON-SPINE-BOUNDARY-01 - Repair Remaining Boundary Imports and Full Proof`
