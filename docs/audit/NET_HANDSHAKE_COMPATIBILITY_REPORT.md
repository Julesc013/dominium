Status: DERIVED
Last Reviewed: 2026-02-16
Supersedes: none
Superseded By: none
Version: 1.0.0
Scope: MP-2 transport abstraction + deterministic handshake compatibility gate.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Net Handshake Compatibility Report

## Supported Transports
1. `transport.loopback` (implemented)
2. `transport.tcp` (stub, deterministic refusal)
3. `transport.udp` (stub, deterministic refusal)

## Deterministic Handshake Acceptance Matrix
| Client Input | Server Policy | Expected Result | Refusal Code |
| --- | --- | --- | --- |
| Matching `pack_lock_hash` + matching registries + allowed policies | `server.policy.private.default` | Accept | N/A |
| `pack_lock_hash` mismatch | Any | Refuse | `refusal.net.handshake_pack_lock_mismatch` |
| Registry hash mismatch | Any | Refuse | `refusal.net.handshake_registry_hash_mismatch` |
| Unsupported schema versions | Any | Refuse | `refusal.net.handshake_schema_version_mismatch` |
| Replication/anti-cheat policy not allowed by server policy | Any | Refuse | `refusal.net.handshake_policy_not_allowed` |
| SecureX policy mismatch or unsigned packs on strict policy | `server.policy.ranked.strict` | Refuse | `refusal.net.handshake_securex_denied` |

## Policy Selection Behavior
1. Client requests `requested_replication_policy_id` + `anti_cheat_policy_id`.
2. Server validates policies strictly against:
   - `build/registries/net_replication_policy.registry.json`
   - `build/registries/anti_cheat_policy.registry.json`
   - `build/registries/net_server_policy.registry.json`
3. Server law profile is selected authoritatively from server policy `allowed_law_profile_ids`.
4. All refusal payloads follow `docs/contracts/refusal_contract.md`.

## Session Pipeline Wiring
1. `stage.net_handshake` is implemented and emits deterministic handshake artifact under `saves/<save_id>/run_meta/`.
2. `stage.net_sync_baseline` remains stubbed and returns deterministic refusal:
   - `refusal.not_implemented.net_transport`
3. `stage.net_join_world` remains stubbed and returns deterministic refusal:
   - `refusal.not_implemented.net_transport`

## Command Surfaces
1. `tools/net/net_cli.py`
   - `net.connect`
   - `net.handshake`
   - `net.status`
   - `net.disconnect`
2. `tools/net/tool_net_loopback_sim.py`
   - Deterministic N-client loopback handshake harness.

## Determinism Notes
1. Handshake artifacts are canonical JSON and hash-stable for identical inputs.
2. Transport latency/order does not affect accept/refuse decisions.
3. Run-meta timestamps are informational and excluded from handshake artifact hash semantics.

## Stubbed Scope (By Design)
1. Baseline sync transport (`stage.net_sync_baseline`)
2. World join transport (`stage.net_join_world`)
3. Full replication stream (lockstep broadcast / deltas)
4. Matchmaking and NAT traversal

## Cross-References
- `docs/net/TRANSPORT_ABSTRACTION.md`
- `docs/net/HANDSHAKE_AND_COMPATIBILITY.md`
- `tools/xstack/sessionx/net_handshake.py`
- `tools/net/net_cli.py`
- `tools/net/tool_net_loopback_sim.py`
