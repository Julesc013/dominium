Status: DERIVED
Last Reviewed: 2026-02-15
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to canon, glossary, session pipeline registry contract, lockfile contract, and multiplayer net schemas v1.0.0.
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Multiplayer Contract Foundation Report

## Scope
This report captures MP-1/9 deliverables: multiplayer canonical contract artifacts only.
No network transport, matchmaking, client prediction, embodiment, or simulation semantic changes are implemented.

## Canon + Invariant Alignment
- Canon references:
  - `docs/canon/constitution_v1.md` (A1, A2, A3, A7, A8, A9, A10; E2, E5, E6, E7; C1-C4)
  - `docs/canon/glossary_v1.md` (AuthorityContext, LawProfile, Lens, PerceivedModel, Refusal, Determinism)
- AGENTS constraints upheld:
  - no mode flags
  - process-only mutation unchanged
  - policy-driven selection by IDs
  - deterministic ordering preserved

## Schemas Added
Canonical schema contracts introduced in `schema/net/` and `schemas/`:

1. `schema/net/intent_envelope.schema`
2. `schema/net/tick_intent_list.schema`
3. `schema/net/hash_anchor_frame.schema`
4. `schema/net/snapshot.schema`
5. `schema/net/delta.schema`
6. `schema/net/perceived_delta.schema`
7. `schema/net/handshake.schema`
8. `schema/net/anti_cheat_event.schema`
9. `schemas/net_intent_envelope.schema.json`
10. `schemas/net_tick_intent_list.schema.json`
11. `schemas/net_hash_anchor_frame.schema.json`
12. `schemas/net_snapshot.schema.json`
13. `schemas/net_delta.schema.json`
14. `schemas/net_perceived_delta.schema.json`
15. `schemas/net_handshake.schema.json`
16. `schemas/net_anti_cheat_event.schema.json`

Derived registry output schemas added:

1. `schemas/net_replication_policy_registry.schema.json`
2. `schemas/net_resync_strategy_registry.schema.json`
3. `schemas/anti_cheat_policy_registry.schema.json`
4. `schemas/anti_cheat_module_registry.schema.json`

CompatX registry was updated for all new schema IDs.

## Data Registries Added
Source policy registries:

1. `data/registries/net_replication_policy_registry.json`
2. `data/registries/net_resync_strategy_registry.json`
3. `data/registries/anti_cheat_policy_registry.json`
4. `data/registries/anti_cheat_module_registry.json`

Derived registry outputs (via `registry_compile`):

1. `build/registries/net_replication_policy.registry.json`
2. `build/registries/net_resync_strategy.registry.json`
3. `build/registries/anti_cheat_policy.registry.json`
4. `build/registries/anti_cheat_module.registry.json`

Lockfile integration:
- New required hashes in `build/lockfile.json.registries`:
  - `net_replication_policy_registry_hash`
  - `net_resync_strategy_registry_hash`
  - `anti_cheat_policy_registry_hash`
  - `anti_cheat_module_registry_hash`

## Policy Matrix (A/B/C)
Replication policies:

1. `policy.net.lockstep`
   - features: `tick_ledger`, `hash_anchors`
   - ranked: allowed
   - resync strategy: `resync.lockstep.replay_intents`
2. `policy.net.server_authoritative`
   - features: `perceived_deltas`, `snapshots`, `hash_anchors`
   - ranked: allowed
   - resync strategy: `resync.authoritative.snapshot`
3. `policy.net.srz_hybrid`
   - features: `shard_routing`, `tick_ledger`, `perceived_deltas`, `hash_anchors`
   - ranked: allowed
   - resync strategy: `resync.hybrid.shard_snapshot`

## Anti-Cheat Modules and Policies
Anti-cheat modules:

1. `ac.module.input_integrity`
2. `ac.module.sequence_integrity`
3. `ac.module.authority_integrity`
4. `ac.module.state_integrity`
5. `ac.module.replay_protection`
6. `ac.module.behavioral_detection`
7. `ac.module.client_attestation` (explicitly optional/off unless policy enables)

Anti-cheat policies:

1. `policy.ac.detect_only`
2. `policy.ac.casual_default`
3. `policy.ac.rank_strict` (`required_for_ranked=true`)
4. `policy.ac.private_relaxed`

## Refusal Codes Added
Network compatibility/security refusal IDs added to `docs/contracts/refusal_contract.md`:

1. `refusal.net.handshake_pack_lock_mismatch`
2. `refusal.net.handshake_registry_hash_mismatch`
3. `refusal.net.handshake_schema_version_mismatch`
4. `refusal.net.handshake_policy_not_allowed`
5. `refusal.net.handshake_securex_denied`
6. `refusal.net.envelope_invalid`
7. `refusal.net.sequence_violation`
8. `refusal.net.replay_detected`
9. `refusal.net.authority_violation`
10. `refusal.net.shard_target_invalid`
11. `refusal.net.resync_required`
12. `refusal.ac.policy_violation`
13. `refusal.ac.rank_policy_required`
14. `refusal.ac.attestation_missing`

## Session Pipeline Structural Integration
Added canonical session stages:

1. `stage.net_handshake`
2. `stage.net_sync_baseline`
3. `stage.net_join_world`

Added pipeline:

1. `pipeline.client.multiplayer_stub`
   - deterministic stage chain includes net stages before warmup.
   - transport remains stubbed by extension metadata.

Default singleplayer pipeline remains unchanged.

## Guardrails
RepoX invariants added:

1. `INV-NET-SCHEMAS-VALID`
2. `INV-NET-POLICY-REGISTRIES-VALID`
3. `INV-NO-HARDCODED-NET-POLICY-FLAGS`
4. `INV-NO-TRUTH-OVER-NET`

AuditX analyzers added:

1. `E1_NET_POLICY_DRIFT`
2. `E2_TRUTH_OVER_NET_SMELL`

## Test Scaffolding Added
Contract-only deterministic tests:

1. `testx.net.schemas_validate`
2. `testx.net.policy_registries_validate`
3. `testx.net.lockfile_includes_net_registries`
4. `testx.net.refusal_codes_present`
5. `testx.net.pipeline_has_net_stages`
6. `testx.net.policy_matrix_rules`

## Stubbed (Explicit Non-Goals)
Not implemented in MP-1:

1. network transport implementation
2. matchmaking/session discovery
3. client prediction/reconciliation
4. embodiment/character controllers
5. replication runtime behavior beyond schema/registry/stage contracts

## Cross-References
- `docs/net/MULTIPLAYER_MODEL_OVERVIEW.md`
- `docs/net/REPLICATION_POLICIES.md`
- `docs/net/HANDSHAKE_AND_COMPATIBILITY.md`
- `docs/net/ANTI_CHEAT_POLICY_FRAMEWORK.md`
- `docs/net/EPISTEMICS_OVER_NETWORK.md`
- `docs/contracts/refusal_contract.md`
- `data/registries/session_stage_registry.json`
- `data/registries/session_pipeline_registry.json`
