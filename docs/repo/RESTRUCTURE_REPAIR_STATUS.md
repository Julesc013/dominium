Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none

# Restructure Repair Status

Latest task: `POST-RESTRUCTURE-REPAIR-SEMANTIC-LINTS`.

Result: PARTIAL, with naming law locked, CTest sharding honest, and semantic lint blockers resolved.

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
- `tools_auditx` no longer blocks the 300 second fast lane after `TEST-PERF-01`; AuditX is split into explicit `audit`/`auditx`/`slow`/`nightly` CTest shards with a 1200 second timeout.
- The tracked `.aide/reports/file-quality-ledger.json` large-file policy remains unresolved.
- The first two repair evidence commits failed AIDE commit-message policy and were not amended; the follow-up commit records the warnings.
- Existing naming conflicts are classified by NAME-00 but not moved or rewritten.

## Next Task

`MOVE-SCRIPT-00 - Generate Deterministic Bad-Root Router and Dry-Run Move Plan`

DOE-00 is not ready. Feature implementation remains blocked.

## NAME-00 Update

NAME-00 added `contracts/repo/naming.contract.toml`, human naming docs, warning-oriented naming validators, and conflict evidence under `.aide/reports/NAME-00-*`.

The naming canon does not authorize moves. Future MOVE-BULK B-G refinement must use the NAME-00 target grammar and keep planned internal renames as future work only.

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
