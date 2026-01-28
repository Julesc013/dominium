# Performance Proof (PERF1)

Status: binding.
Scope: formal statement and evidence for the constant-cost guarantee under PERF-1.

## Claim

For a fixed set of active Tier-2 domains, per-tick simulation work is bounded
independently of total world size, history length, or collapsed domain count.
Budget admission and deterministic scheduling enforce this guarantee.

## Evidence

PERF-1 provides data-only fixtures and deterministic tests that exercise
worst-case patterns without altering simulation semantics:

- Galaxy-scale civilization (many collapsed domains, dense macro activity).
- Local density extreme (one region with maximal assemblies/processes).
- Deep history (long macro timelines with heavy compaction).
- Thrash attempt (repeated collapse/expand requests under budgets).
- MMO-style load (many intents and cross-shard messages).

Evidence is recorded in:

- `tests/fixtures/perf/*/metrics/` for fixture metrics.
- `tests/perf/perf_fixture_contracts.py` for deterministic invariance.
- `tests/perf/perf_budget_gate_tests.py` and `tools/ci/perf_budget_check.py`
  for budget regression gates.

## What is not guaranteed

- Wall-clock performance on any specific hardware.
- Unlimited active domains or unbounded per-tick work.
- Performance of non-deterministic or non-budgeted workloads.
- Rendering throughput, GPU timing, or client-side presentation costs.

## Related contracts

- `docs/architecture/CONSTANT_COST_GUARANTEE.md`
- `docs/architecture/SCALING_MODEL.md`
- `docs/architecture/BUDGET_POLICY.md`
- `docs/architecture/COLLAPSE_EXPAND_CONTRACT.md`
- `docs/architecture/DETERMINISTIC_ORDERING_POLICY.md`
- `docs/policies/PERF_BUDGETS.md`
