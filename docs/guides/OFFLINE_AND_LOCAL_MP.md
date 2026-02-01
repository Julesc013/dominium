Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Offline + Local Multiplayer Parity (MP0)

This document defines the MP0 parity guarantees for LIFE and CIV systems across:
- Offline singleplayer (loopback server-auth)
- Local multiplayer lockstep
- Local multiplayer server-auth

## Supported modes
1) Loopback server-auth (default singleplayer)
   - Server and client run in the same process.
   - Authoritative logic is identical to multiplayer.

2) Local lockstep
   - Peers simulate identically from the same command stream.
   - Determinism gates apply as in DET*.

3) Local server-auth
   - Server owns authority.
   - Clients receive state updates only.
   - Client-side authority is forbidden for LIFE/CIV decisions.

## Continuation parity
- Continuation selections are commands in lockstep.
- Server validates and applies continuation in server-auth.
- Clients cannot force continuation binding changes.

## CIV0a parity
- Consumption is event-driven in all modes.
- Production actions are commands in all modes.
- Starvation/dehydration uses the same death hooks.

## Epistemic parity
- All modes use the same epistemic pipeline.
- Local MP does not expose hidden information by default.
- Spectator privileges require explicit capabilities.

## Determinism guarantees
- Loopback uses the same authoritative path as multiplayer.
- Lockstep peers converge on identical hashes.
- Server-auth clients accept authoritative state without divergence.

## MP0 fixtures and CI
- Determinism fixtures include CIV0a Survival + MP0 parity runs.
- CI checks enforce:
  - MP0-PARITY-001 (loopback equivalence)
  - MP0-LOCKSTEP-001 (lockstep parity)
  - MP0-SERVERAUTH-001 (server-auth parity)