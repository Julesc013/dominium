Status: CANONICAL
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none

# TestX Architecture

## Scope

TestX is the behavioral proof layer for Dominium. It validates invariant compliance, determinism envelopes, workspace isolation, and regression locks using deterministic test execution contracts.

## Execution Model

XStack runs TestX through sharded group registries, not monolithic test targets:

- Group registry: `data/registries/testx_groups.json`
- Group runner: `scripts/dev/run_xstack_group_tests.py`
- Planner mapping: `tools/xstack/core/impact_graph.py` -> `tools/xstack/core/plan.py`

Gate profiles map to groups:

- `FAST`: only impacted fast groups (plus required invariants).
- `STRICT_LIGHT`: invariants + impacted runtime verification groups.
- `STRICT_DEEP`: strict-light behavior when schema/governance paths are touched.
- `FULL`: impacted shards across all required groups.
- `FULL_ALL`: explicit all-shard execution.

## `testx_all` Monolith Policy

`testx_all` is demoted from local developer workflows.

- Local development: use sharded gate profiles (`verify`, `strict`, `full`).
- CI or explicit legacy request: monolith may still be used for compatibility checks.
- Gate profiles must not call `testx_all` directly.

## Impact-Driven Selection

RepoX emits `docs/audit/proof_manifest.json` and XStack builds an impact graph from changed paths.
Test group selection is deterministic and reproducible for the same repo state hash.

## Determinism Envelopes

TestX includes dedicated envelope checks for:

- thread-count variance
- SRZ partition variance
- budget/fidelity selection variance
- named RNG stream stability

Envelope checks are non-semantic proofs that canonical outputs remain stable under allowed execution variance.

## Artifact Contract

Determinism checks operate on canonical artifacts only. TestX ignores RUN_META artifacts during canonical hash comparisons and validates that canonical artifacts do not carry timestamp/run-meta keys.

## Workspace Isolation Proof

TestX validates that workspace-scoped outputs remain isolated under `out/build/<WS_ID>/` and `dist/ws/<WS_ID>/`, and that gate policy commands avoid hardcoded global output paths.

## Regression Lock Philosophy

Historical blocker classes are encoded as explicit regression tests under `tests/regression/historical_blockers/`. Each blocker family has a stable, repeatable proof that failure classes cannot silently recur.
