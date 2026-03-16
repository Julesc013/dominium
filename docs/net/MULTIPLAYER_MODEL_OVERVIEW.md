Status: DERIVED
Last Reviewed: 2026-02-15
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, and SRZ/hash anchor contracts.
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Multiplayer Model Overview

## Purpose
Define canonical multiplayer primitives without binding to one transport model.
Multiplayer variants are policy selections over shared deterministic artifacts.

## Shared Primitives

1. `IntentEnvelope`:
   - Deterministic, authority-scoped intent container.
   - Routed by shard/peer identity; no implicit mutation semantics.
2. `TickLedger`:
   - Ordered per-tick intent lists plus ordering rule identity.
   - Source of replayability and conflict diagnostics.
3. Snapshot/Delta artifacts:
   - Snapshot: deterministic point-in-time state reference (hash + artifact ref).
   - Delta: deterministic transition slice between ticks.
4. Perceived transport contract:
   - Network payloads carry `PerceivedModel` deltas or references, never direct Truth payloads.
5. `HashAnchorFrame`:
   - Per-tick shard hashes and composite hash chain for resync/proof.

## Policy Families Over Shared Primitives

1. Lockstep deterministic (`policy.net.lockstep`)
2. Server authoritative replication (`policy.net.server_authoritative`)
3. SRZ hybrid deterministic shard authority (`policy.net.srz_hybrid`)

These are not separate engines; they are registry-declared policies over one canonical artifact layer.

## Determinism Invariants

1. Network timing never changes authoritative truth outcomes.
2. Envelope ordering remains deterministic for identical `(tick, sequence, policy)`.
3. Hash anchors remain reproducible across replay for identical envelope ledgers.
4. Transport retries/reordering may delay presentation but must not alter commit legality.

## Non-Goals (This Prompt)

1. No transport socket/protocol implementation.
2. No client prediction/reconciliation logic.
3. No matchmaking/lobby layer.
4. No embodiment/gameplay semantic changes.

## Example

```json
{
  "replication_policy_id": "policy.net.lockstep",
  "tick": 120,
  "ordered_envelope_ids": [
    "env.peer.alpha.120.0001",
    "env.peer.bravo.120.0002"
  ],
  "composite_hash": "f2f5f6bb0af6bdbecfdb9bc92e6c8edee2284608ddf58f40f95f88c213bb7648"
}
```

## Cross-References

- `docs/net/REPLICATION_POLICIES.md`
- `docs/net/HANDSHAKE_AND_COMPATIBILITY.md`
- `docs/net/EPISTEMICS_OVER_NETWORK.md`
- `docs/architecture/srz_contract.md`
- `docs/architecture/hash_anchors.md`

## TODO

- Add transport binding matrix (UDP/reliable relay/quic) as non-canonical implementation guidance.
- Add multi-region latency budget table for future PerformX integration.
