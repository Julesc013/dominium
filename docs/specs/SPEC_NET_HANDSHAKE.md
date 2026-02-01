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
- Rules, policy, and interpretation defined by this spec.
- Implementation lives under `game/` (rules/content/ui as applicable).

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
# SPEC_NET_HANDSHAKE — Session Handshake (Framed TLV, Authoritative)

This spec defines the on-wire handshake used by the deterministic netcode
session model.

Scope:

- message framing (`DNM` header)
- handshake and handshake-reply payload fields (TLV)
- compatibility / rejection behavior at a high level

Out of scope:

- platform transport (TCP/UDP/etc)
- game content negotiation beyond the fields listed here

## 1) Framing (DNM v1)

All netcode messages use the `DNM` frame header (see `source/domino/net/d_net_proto.{h,c}`):

- Magic: ASCII `DNM`
- Frame version: `1`
- Message type: `d_net_msg_type` (`HANDSHAKE`, `HANDSHAKE_REPLY`, etc.)
- Payload length + payload bytes

The payload is a TLV record stream (u32 tag + u32 len + bytes), little-endian.

## 2) Handshake payload (HANDSHAKE_V1)

Schema identifiers:

- Protocol version: `D_NET_PROTO_VERSION` (`source/domino/net/d_net_schema.h`)
- Handshake schema id: `D_NET_SCHEMA_HANDSHAKE_V1`

Required TLV fields (u32 values, little-endian):

- `D_NET_TLV_HANDSHAKE_SUITE_VERSION`
- `D_NET_TLV_HANDSHAKE_CORE_VERSION`
- `D_NET_TLV_HANDSHAKE_NET_PROTO_VER`

Optional TLV fields:

- `D_NET_TLV_HANDSHAKE_COMPAT_PROFILE` (product-defined)
- `D_NET_TLV_HANDSHAKE_ROLE` (session role: single/host/client)

Unknown tags must be skipped safely.

## 3) Handshake reply payload (HANDSHAKE_REPLY_V1)

Schema identifier:

- Handshake reply schema id: `D_NET_SCHEMA_HANDSHAKE_REPLY_V1`

Required TLV fields:

- `D_NET_TLV_HANDSHAKE_REPLY_RESULT` (`0` = ok, non-zero = reject)

Optional TLV fields:

- `D_NET_TLV_HANDSHAKE_REPLY_REASON_CODE` (product-defined)
- `D_NET_TLV_HANDSHAKE_REPLY_ASSIGNED_PEER`
- `D_NET_TLV_HANDSHAKE_REPLY_SESSION_ID`
- `D_NET_TLV_HANDSHAKE_REPLY_TICK_RATE`
- `D_NET_TLV_HANDSHAKE_REPLY_TICK`

## 4) Compatibility and rejection

- Handshake negotiation is a **pre-snapshot** phase.
- The product layer (Dominium) may reject peers based on suite/core/protocol
  versions and compatibility profile values.
- Rejections must be explicit (non-zero `RESULT` + optional `REASON_CODE`).

## Related docs

- `docs/specs/SPEC_CONTAINER_TLV.md` (canonical TLV encoding rules)
- `docs/specs/SPEC_NETCODE.md` (session model overview)
- `docs/specs/SPEC_PACKETS.md` (deterministic packet taxonomy)