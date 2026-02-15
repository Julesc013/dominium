Status: DERIVED
Version: 1.0.0
Last Reviewed: 2026-02-15
Compatibility: Bound to Session pipeline contract, lockfile contract, CompatX schema registry, and refusal contract.

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
7. `server_law_profile_id`
8. peer IDs and protocol version

## Deterministic Handshake Rules

1. No silent negotiation:
   - Any compatibility mismatch is explicit `result=refuse`.
2. Negotiation order is deterministic:
   - Compare lock hash -> registries -> schema versions -> policy allowability -> securex gates.
3. Handshake artifacts are immutable run records once accepted/refused.

## Session Pipeline Integration (Structural)

Optional multiplayer stage chain:

1. `stage.net_handshake`
2. `stage.net_sync_baseline`
3. `stage.net_join_world`

Rules:

1. Stages are enabled only when SessionSpec selects multiplayer transport endpoint metadata.
2. In current stub state, missing transport plugin must refuse deterministically (`refusal.not_implemented` family).
3. Default singleplayer pipeline remains unchanged.

## Refusal Codes (Compatibility)

1. `refusal.net.handshake_pack_lock_mismatch`
2. `refusal.net.handshake_registry_hash_mismatch`
3. `refusal.net.handshake_schema_version_mismatch`
4. `refusal.net.handshake_policy_not_allowed`
5. `refusal.net.handshake_securex_denied`
6. `refusal.net.resync_required`

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
- `data/registries/session_stage_registry.json`
- `data/registries/session_pipeline_registry.json`
- `docs/contracts/refusal_contract.md`

## TODO

- Add handshake capability extension map for future secure transport module negotiation.
