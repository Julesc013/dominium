Status: DERIVED
Version: 1.0.0
Last Reviewed: 2026-02-15
Scope: MP-5/9 deterministic SRZ hybrid replication baseline.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# SRZ Hybrid Baseline Report

## Summary
- Replication policy `policy.net.srz_hybrid` is integrated and marked implemented.
- Single-process multi-shard coordination is active for deterministic development/runtime validation.
- Hybrid net baseline/join stages are wired in session pipeline and produce deterministic run artifacts.

## Shard Map Defaults
- Registry: `data/registries/shard_map_registry.json`
- Default maps:
  - `shard_map.default.single_shard`
  - `shard_map.default.single_process_two_shards`
- Lockfile/registry outputs now include `shard_map_registry_hash`.

## Routing Rules
- Primary router: `src/net/srz/routing.py`
- Deterministic targeting order:
  1. explicit `target_shard_id` if valid
  2. derive from object/site ownership via shard map
  3. fallback `shard.0`
- Multi-target intents split into deterministic sub-envelopes with parent linkage.

## Barrier and Ordering Rules
- Coordinator: `src/net/srz/shard_coordinator.py`
- Per tick:
  1. collect and route envelopes
  2. shard-local `read -> propose -> resolve -> commit`
  3. cross-shard proposal barrier
  4. deterministic resolve ordering by stable keys
  5. per-shard hash + composite hash frame emission
- Unsupported cross-shard direct writes refuse with `refusal.net.cross_shard_unsupported`.

## Perception Interest Policy
- Registry: `data/registries/perception_interest_policy_registry.json`
- Default policies:
  - `policy.perception.lab.default`
  - `policy.perception.lab.minimal`
- Network deltas are filtered by law/lens/authority plus perception-interest policy.
- Missing policy refuses with `refusal.net.perception_policy_missing`.

## Hash Anchor Validation
- Hybrid coordinator emits per-shard hashes and deterministic composite hash per tick.
- Session baseline/join use snapshot references and hash-anchor continuity.
- Lockfile includes:
  - `shard_map_registry_hash`
  - `perception_interest_policy_registry_hash`

## Test Coverage
- `testx.net.srz_hybrid.two_shard_equivalence`
- `testx.net.srz_hybrid.cross_shard_routing_determinism`
- `testx.net.srz_hybrid.client_interest_filter_no_leak`
- `testx.net.srz_hybrid.resync_snapshot_stub`
- `testx.net.pipeline_net_handshake_stage_srz_hybrid`

## Guardrails
- RepoX:
  - `INV-SRZ-HYBRID-ROUTING-USES-SHARD-MAP`
  - `INV-NO-CROSS-SHARD-DIRECT-WRITES`
  - `INV-NO-TRUTH-OVER-NET`
- AuditX analyzers:
  - `auditx.cross_shard_write_smell`
  - `auditx.shard_map_drift`

## Known Limitations
- Multi-process/multi-machine shard authority transport remains stubbed for future prompts.
- Dynamic shard migration/load balancing is deferred.
- Cross-shard direct writes remain explicitly unsupported in v1 baseline.

## Cross-References
- `docs/net/SRZ_HYBRID_POLICY.md`
- `docs/net/REPLICATION_POLICIES.md`
- `docs/net/HANDSHAKE_AND_COMPATIBILITY.md`
- `docs/contracts/refusal_contract.md`
- `schemas/shard_map.schema.json`
