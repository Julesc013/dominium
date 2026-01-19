--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. Engine provides generic primitives only if referenced.

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
# SPEC_QOS_ASSISTANCE — QoS and Assistance Negotiation

## Scope
Defines non-sim quality-of-service (QoS) negotiation between client and server.
QoS affects presentation cadence, detail, and assistance only. It MUST NOT change
authoritative simulation behavior, tick scheduling, or command ordering.

## Invariants
- QoS is non-authoritative and never mutates simulation state.
- QoS does not change session authority mode or tick rate.
- Unknown tags are ignored; skip-unknown is required.
- Any sim-affecting request is refused (see Refusal rules).

## Transport
- QoS messages are carried in `D_NET_MSG_QOS` frames.
- Payload is a TLV stream (u32 tag + u32 length + payload), little-endian.
- Schema version tag MUST be present.

## Message kinds
`DOM_QOS_TLV_KIND`:
- `1` CLIENT_HELLO: client perf caps + preferences (perf-only).
- `2` SERVER_POLICY: server-selected effective params.
- `3` CLIENT_STATUS: client status + reduction request.

## TLV tags (v2)
- `DOM_QOS_TLV_SCHEMA_VERSION` (1): u32, must be `2`.
- `DOM_QOS_TLV_KIND` (2): u32, one of the kinds above.

Client caps (CLIENT_HELLO):
- `DOM_QOS_TLV_CAPS_PERF_DIGEST64` (10): u64, PERF_CAPS digest only.
- `DOM_QOS_TLV_CAPS_PREFERRED_PROFILE` (11): u32, preferred tier/profile hint.
- `DOM_QOS_TLV_CAPS_MAX_SNAPSHOT_HZ` (12): u32, max snapshot cadence.
- `DOM_QOS_TLV_CAPS_MAX_DELTA_DETAIL` (13): u32, cap on detail (0..100).
- `DOM_QOS_TLV_CAPS_MAX_INTEREST_RADIUS_M` (14): u32, max interest radius in meters.
- `DOM_QOS_TLV_CAPS_DIAGNOSTIC_RATE_CAP` (15): u32, cap on diagnostics rate (hash/exchange cadence).
- `DOM_QOS_TLV_CAPS_ASSIST_FLAGS` (16): u32, opt-in assist flags (optional).

Server policy (SERVER_POLICY):
- `DOM_QOS_TLV_POLICY_SNAPSHOT_HZ` (20): u32, snapshot cadence (server-auth) or diagnostics cadence (lockstep).
- `DOM_QOS_TLV_POLICY_DELTA_DETAIL` (21): u32, delta/detail scale (0..100).
- `DOM_QOS_TLV_POLICY_INTEREST_RADIUS_M` (22): u32, interest radius in meters.
- `DOM_QOS_TLV_POLICY_RECOMMENDED_PROFILE` (23): u32, recommended tier/profile hint.
- `DOM_QOS_TLV_POLICY_SERVER_LOAD_HINT` (24): u32, 0=nominal,1=busy,2=overloaded.
- `DOM_QOS_TLV_POLICY_ASSIST_FLAGS` (25): u32, allowed assist flags (optional).

Client status (CLIENT_STATUS):
- `DOM_QOS_TLV_STATUS_RENDER_FPS_AVG` (30): u32, recent fps average.
- `DOM_QOS_TLV_STATUS_FRAME_TIME_MS_AVG` (31): u32, recent frame-time average (ms).
- `DOM_QOS_TLV_STATUS_BACKLOG_JOBS` (32): u32, pending derived jobs count.
- `DOM_QOS_TLV_STATUS_DERIVED_QUEUE_PRESSURE` (33): u32, 0..100 pressure gauge.
- `DOM_QOS_TLV_STATUS_REQUEST_DETAIL_REDUCTION` (34): u32, 0/1 request to reduce detail.

Assist flags (bitmask):
- `1` LOCAL_MESH: client can build presentation meshes locally.
- `2` LOCAL_CACHE: client can build local caches (surface/tiles) locally.

## Semantics
- The server computes an effective policy by clamping server policy by client
  caps, then applying client status reductions and server load hints. This
  affects presentation only.
- `snapshot_hz` controls snapshot cadence (server-auth) or diagnostics cadence
  (lockstep), not simulation tick rate.
- `delta_detail` and `interest_radius_m` affect what is sent and rendered, not
  authoritative state.
- Assist flags allow clients to build derived artifacts locally; the server may
  omit derived artifacts when assist flags are granted.
- QoS requests are advisory; the server remains authoritative.

## Refusal rules
- Any field that would alter simulation authority, tick ordering, or command
  processing MUST be rejected. Implementations SHOULD log and MAY disconnect on
  repeated violations.
- Absolute paths or content identity changes are not valid QoS fields and MUST
  be refused.

## Audit requirements
- Each applied policy change MUST emit a deterministic audit entry containing:
  message kind, caps/status inputs, effective policy, and reason flags.
- Audit output MUST be stable for identical inputs.
