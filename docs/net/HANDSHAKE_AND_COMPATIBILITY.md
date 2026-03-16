Status: DERIVED
Last Reviewed: 2026-02-16
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to Session pipeline contract, lockfile contract, CompatX schema registry, and refusal contract.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Handshake and Compatibility

## Purpose
Define deterministic multiplayer compatibility handshake artifacts and refusal behavior.

## Handshake Required Fields

1. `pack_lock_hash`
2. registry hash map
3. schema versions map
4. `requested_replication_policy_id`
5. `negotiated_replication_policy_id`
6. `anti_cheat_policy_id`
7. `securex_policy_id`
8. `server_profile_id`
9. `server_law_profile_id`
10. peer IDs and protocol version
11. `extensions.enforce_lod_invariance_strict` (server-profile governed, deterministic boolean)

## Handshake Sequence (Deterministic)

```text
Client                                Server
  |                                     |
  | proto_message(handshake_request)    |
  |------------------------------------>|
  |                                     | validate in fixed order:
  |                                     | 1) pack_lock_hash
  |                                     | 2) registry hashes
  |                                     | 3) schema versions
  |                                     | 4) replication policy allowability
  |                                     | 5) anti-cheat policy allowability/requirement
  |                                     | 6) server profile policy constraints
  |                                     | 7) SecureX policy requirements
  |                                     | 8) server law_profile selection
  | proto_message(handshake_response)   |
  |<------------------------------------|
  |                                     |
```

Handshake result is content-driven and deterministic. Wall-clock timing must not influence accept/refuse decisions.

## Deterministic Handshake Rules

1. No silent negotiation:
   - Any compatibility mismatch is explicit `result=refuse`.
2. Negotiation order is deterministic:
   - Compare lock hash -> registries -> schema versions -> policy allowability -> server profile gates -> securex gates.
3. Handshake artifacts are immutable run records once accepted/refused.
4. Ranked/server-governed LOD epistemic strictness is advertised by handshake extension:
   - `extensions.enforce_lod_invariance_strict=true` means server expects strict `refusal.ep.lod_information_gain` behavior on violations.

## Session Pipeline Integration (Structural)

Optional multiplayer stage chain:

1. `stage.net_handshake`
2. `stage.net_sync_baseline`
3. `stage.net_join_world`

Rules:

1. Stages are enabled only when SessionSpec selects multiplayer transport endpoint metadata.
2. Deterministic stage execution is policy-driven:
   - `policy.net.server_authoritative`: `stage.net_sync_baseline` and `stage.net_join_world` are implemented.
   - `policy.net.srz_hybrid`: `stage.net_sync_baseline` and `stage.net_join_world` are implemented using shard snapshot baseline artifacts.
   - `policy.net.lockstep`: baseline/join stages remain stubbed and refuse with `refusal.not_implemented.net_transport`.
3. Default singleplayer pipeline remains unchanged.
4. Canonical multiplayer stub pipeline id is `pipeline.client.multiplayer_stub`.
5. Net stage order is fixed: `stage.net_handshake -> stage.net_sync_baseline -> stage.net_join_world`.
6. `stage.net_handshake` is executable in MP-2.
7. `stage.net_sync_baseline` writes deterministic baseline artifacts (snapshot + anchor summary) before join.
8. `stage.net_join_world` validates negotiated policy and join snapshot, then binds the client to baseline PerceivedModel state.
9. For `policy.net.srz_hybrid`, baseline artifacts include `shard_map_id`, `perception_interest_policy_id`, and deterministic `snapshot_ids`.

## CLI Surfaces

1. `tools/net/net_cli.py --session-spec <path> net.connect --endpoint <endpoint>`
2. `tools/net/net_cli.py --session-spec <path> net.handshake --policy <policy_id> --anti-cheat <policy_id>`
3. `tools/net/net_cli.py --session-spec <path> net.status`
4. `tools/net/net_cli.py --session-spec <path> net.disconnect`
5. `tools/net/tool_net_loopback_sim.py --session-spec <path> --clients <N>`

## Refusal Codes (Compatibility)

1. `refusal.net.handshake_pack_lock_mismatch`
2. `refusal.net.handshake_registry_hash_mismatch`
3. `refusal.net.handshake_schema_version_mismatch`
4. `refusal.net.handshake_policy_not_allowed`
5. `refusal.net.handshake_securex_denied`
6. `refusal.net.resync_required`
7. `refusal.net.resync_snapshot_missing`
8. `refusal.net.join_snapshot_invalid`
9. `refusal.net.join_policy_mismatch`
10. `refusal.net.cross_shard_unsupported`
11. `refusal.net.perception_policy_missing`

## Refusal Mapping (Deterministic)

1. `refusal.net.handshake_pack_lock_mismatch`
Cause: client/server `pack_lock_hash` differs.
Remediation: rebuild/install matching bundle lockfile.

2. `refusal.net.handshake_registry_hash_mismatch`
Cause: any required registry hash differs.
Remediation: recompile registries and reconnect with matching dist.

3. `refusal.net.handshake_schema_version_mismatch`
Cause: handshake-declared schema version unsupported by CompatX.
Remediation: migrate/downgrade schema versions to supported set.

4. `refusal.net.handshake_policy_not_allowed`
Cause: requested replication/anti-cheat/law profile not permitted by server profile registry.
Remediation: request values allowed by the selected `server_profile_id`.

5. `refusal.net.handshake_securex_denied`
Cause: server SecureX requirements not satisfied.
Remediation: connect with required signed-pack/security posture.

6. `refusal.net.cross_shard_unsupported`
Cause: process envelope resolves to shard ownership mismatch and cross-shard direct write path is not declared.
Remediation: route process to owning shard or declare an explicit cross-shard transition contract.

7. `refusal.net.perception_policy_missing`
Cause: server policy does not resolve a valid perception-interest policy for SRZ hybrid replication.
Remediation: set `extensions.perception_interest_policy_id` in server policy and rebuild registries/lockfile.

## Example

```json
{
  "result": "refuse",
  "refusal": {
    "reason_code": "refusal.net.handshake_pack_lock_mismatch",
    "message": "client pack_lock_hash does not match server lock hash",
    "remediation_hint": "Install matching bundle/lockfile and retry handshake.",
    "relevant_ids": {
      "client_peer_id": "peer.client.alpha",
      "server_peer_id": "peer.server.lab"
    }
  }
}
```

## Cross-References

- `schemas/net_handshake.schema.json`
- `schemas/net_proto_message.schema.json`
- `data/registries/session_stage_registry.json`
- `data/registries/session_pipeline_registry.json`
- `data/registries/net_server_policy_registry.json`
- `data/registries/securex_policy_registry.json`
- `data/registries/server_profile_registry.json`
- `docs/contracts/refusal_contract.md`
- `docs/net/TRANSPORT_ABSTRACTION.md`

## TODO

- Add handshake capability extension map for future secure transport module negotiation.
