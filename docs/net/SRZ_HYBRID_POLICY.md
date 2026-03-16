Status: DERIVED
Last Reviewed: 2026-02-15
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/net/REPLICATION_POLICIES.md`, and deterministic SRZ/hash contracts.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# SRZ Hybrid Policy

## Purpose
Define `policy.net.srz_hybrid` as deterministic shard-authoritative replication over shared multiplayer contracts.

## Authority Model

1. Each shard is authoritative for owned entities/regions declared by `shard_map_id`.
2. Clients submit `intent_envelope` payloads to a gateway/coordinator.
3. Gateway routes envelopes to target shards deterministically.
4. Shards commit only owned-state mutations.
5. Cross-shard direct writes are forbidden in v1; unsupported attempts refuse deterministically.

## Deterministic Routing

1. Explicit target:
   - If `intent_envelope.target_shard_id` is set, it must exist in the active shard map.
   - Unknown target refuses with `refusal.net.shard_target_invalid`.
2. Derived target:
   - If payload references `object_id` or `target_object_id`, route via shard-map ownership.
   - If payload references `site_id` or `target_site_id`, route via shard-map ownership lookup.
   - If no routable target is present, route to `shard.0`.
3. Multi-shard intents:
   - Split into deterministic sub-envelopes ordered by `target_shard_id`.
   - Sub-envelope id = canonical hash of `{parent_envelope_id, target_shard_id}` prefix.
   - Sub-envelopes include `extensions.parent_envelope_id`.

## Tick Coordination

Per tick `T`:

1. Collect routed envelopes for `T` by shard.
2. Each shard executes deterministic phases:
   - `read -> propose -> resolve -> commit`
3. Cross-shard barrier:
   - Exchange cross-shard proposals (metadata only in v1).
   - Resolve with stable key:
     `(tick, target_shard_id, source_shard_id, process_id, deterministic_sequence_number, envelope_id)`.
4. Commit in stable shard order (`shard_id` ascending).
5. Emit per-shard hash anchors.
6. Compute composite hash over sorted shard hashes.

## Client Visibility

1. Network transport carries PerceivedModel deltas only.
2. Perceived payloads are filtered by:
   - `LawProfile`
   - `Lens`
   - `AuthorityContext`
   - `PerceptionInterestPolicy`
3. Truth payload transport is forbidden.

## Resync Strategy

Policy uses `resync.hybrid.shard_snapshot`.

1. On desync, client requests shard-scoped snapshot references for current interest set.
2. Client applies snapshot baseline and replays subsequent perceived deltas.
3. If snapshot artifacts are unavailable, refuse with `refusal.net.resync_required`.

## Perception Interest Management

1. Interest selection is independent from compute ROI.
2. Policy defines max objects per tick and deterministic ordering.
3. Missing policy refuses with `refusal.net.perception_policy_missing`.

## Known Limitations (MP-5)

1. Single-process multi-shard runtime is canonical for now.
2. Multi-process authority endpoints are contract-ready but transport-stubbed.
3. Dynamic shard migration/load balancing is not implemented in this phase.
4. Cross-shard writes remain unsupported unless explicitly declared in future process metadata contracts.

## Refusal Codes

1. `refusal.net.shard_target_invalid`
2. `refusal.net.cross_shard_unsupported`
3. `refusal.net.perception_policy_missing`
4. `refusal.net.resync_required`

## Cross-References

- `docs/net/REPLICATION_POLICIES.md`
- `schemas/shard_map.schema.json`
- `data/registries/shard_map_registry.json`
- `data/registries/perception_interest_policy_registry.json`
- `docs/contracts/refusal_contract.md`
