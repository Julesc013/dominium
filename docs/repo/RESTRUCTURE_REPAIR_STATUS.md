Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none

# Restructure Repair Status

Latest task: `TEST-PERF-01`.

Result: PARTIAL, with naming law locked and CTest sharding now honest.

## Current Green Gates

- AIDE doctor/validate/test/selftest/tools/roots/repo pass.
- Strict layout/root/distribution/component validators pass.
- Focused RepoX passes.
- Smoke CTest passes.
- Fast CTest label passes.
- AuditX slow shard passes.
- Native configure and build-only `ALL_BUILD` pass.
- Product boot, portable projection, and internal pilot release validators pass.
- Frozen contract guard passes.
- Override policy tests pass.
- Replay hash invariance passes.

## Current Blockers

- Full CTest is not green.
- Twenty-three formerly bad roots remain under active exceptions.
- `slice0_hardcoded_ids` still fails on current hardcoded identifiers.
- `slice1_hardcoded_constants` still fails on current domain constants.
- `tools_auditx` no longer blocks the 300 second fast lane after `TEST-PERF-01`; AuditX is split into explicit `audit`/`auditx`/`slow`/`nightly` CTest shards with a 1200 second timeout.
- The tracked `.aide/reports/file-quality-ledger.json` large-file policy remains unresolved.
- The first two repair evidence commits failed AIDE commit-message policy and were not amended; the follow-up commit records the warnings.
- Existing naming conflicts are classified by NAME-00 but not moved or rewritten.

## Next Task

`POST-RESTRUCTURE-REPAIR-SEMANTIC-LINTS - Hardcoded Identifier and Constant Disposition`

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

Full CTest remains not green because `slice0_hardcoded_ids` and `slice1_hardcoded_constants` still fail.
