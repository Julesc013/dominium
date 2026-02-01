Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Deterministic primitives and invariants defined by this spec.
- Implementation lives under `engine/` (public API in `engine/include/`).

GAME:
- None. Game consumes engine primitives where applicable.

TOOLS:
- None. Tools may only consume public APIs if needed.

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
# Netcode (Deterministic Sessions + Commands)

## Goals

- Multiplayer determinism is **input/command-driven**: peers exchange commands, not world state.
- The simulation stays deterministic when all peers start from the same snapshot/save and apply the same command stream.
- The engine core (`source/domino/**`) does **no OS networking**. Network I/O is provided by a thin product/platform transport.

## Session Model

Engine session state is defined in `source/domino/net/d_net_session.h`.

- **Roles**
  - `D_NET_ROLE_SINGLE`: local-only loopback (still uses the command queue path)
  - `D_NET_ROLE_HOST`: authoritative host for session control and command rebroadcast
  - `D_NET_ROLE_CLIENT`: remote participant receiving snapshots and command streams
- **Peers**
  - `d_peer_id` is a stable per-session identifier.
  - Host tracks all peers; clients track at least `{host,self}`.
- **Ticking**
  - Simulation is fixed-tick. `d_sim_step()` increments `tick_index` and applies queued commands at the start of each tick.
  - Commands are scheduled for a future tick using `input_delay_ticks` to absorb latency.

## Deterministic Command Application

At the start of each simulation tick, the engine dequeues all commands for that tick and applies them deterministically:

- Dequeue: `d_net_cmd_dequeue_for_tick(tick, ...)`
- Sort order: `(source_peer, id, schema_id, schema_ver, payload bytes)` in `source/domino/net/d_net_apply.c`
- Apply: schema-specific handlers (currently build + research) or deterministic no-op for unknown schemas

## Protocol Overview

All network messages are framed and the payload is a TLV blob.

- Frame: `source/domino/net/d_net_proto.{h,c}`
  - Magic: `"DNM"`
  - Frame version: `D_NET_PROTO_VERSION` (`docs` refer to framing, not engine ABI)
  - Type: `D_NET_MSG_*`
  - Payload length + bytes
- TLV format: `tag(u32) + len(u32) + payload bytes` (see `source/domino/core/d_tlv_kv.h`)

### Message Types

- `HANDSHAKE` / `HANDSHAKE_REPLY`
- `SNAPSHOT` (existing save blob + tick)
- `CMD` (deterministic command envelope)
- `TICK`, `HASH`, `ERROR` (optional control/debug)

## Handshake + Compatibility

Handshake schemas are defined in `source/domino/net/d_net_schema.h` and encoded/decoded in `source/domino/net/d_net_proto.c`.

Handshake includes:

- suite version
- core version
- net protocol version
- compat profile blob
- role

Host reply includes:

- result (ok/reject) + reason code
- assigned peer id
- session id
- tick rate and current tick

Dominium decides compatibility and may reject a peer before sending a snapshot.

## Snapshot Join

Initial sync uses an existing Dominium save blob (no raw world struct dumps):

- Host sends `SNAPSHOT` containing `{tick, data(save_blob)}`
- Client loads the blob (Dominium save loader), sets `world->tick_count` and `sim->tick_index`, clears command queue, and becomes ready

## Command Encoding

Command payloads are schema-specific TLV (not fixed binary structs).

- Envelope fields (inside `CMD` payload):
  - `CMD_ID`, `CMD_SOURCE`, `CMD_TICK`, `CMD_SCHEMA_ID`, `CMD_SCHEMA_VER`, `CMD_PAYLOAD`
- Schemas and tags:
  - `CMD_BUILD_V1` (`D_NET_SCHEMA_CMD_BUILD_V1`)
  - `CMD_RESEARCH_V1` (`D_NET_SCHEMA_CMD_RESEARCH_V1`)
  - Tags are in `source/domino/net/d_net_schema.h`

## Transport Integration

Engine-only transport surface:

- Register callbacks: `source/domino/net/d_net_transport.h`
  - `send_to_peer(user, peer, data, size)`
  - `broadcast(user, data, size)`
- Product/platform provides sockets and calls `d_net_receive_packet(session, source_peer, data, size)` on inbound packets.

Dominium currently implements a simple TCP transport in `source/dominium/game/dom_game_net.cpp`.