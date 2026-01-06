# SPEC_QOS_ASSISTANCE — QoS and Assistance Negotiation

## Scope
Defines non-sim quality-of-service (QoS) negotiation between client and server.
QoS affects presentation cadence and detail only. It MUST NOT change authoritative
simulation behavior, tick scheduling, or command ordering.

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
- `1` CLIENT_HELLO: client capability caps (perf-only).
- `2` SERVER_POLICY: server-selected effective params.
- `3` CLIENT_STATUS: client status + desired reductions.

## TLV tags (v1)
- `DOM_QOS_TLV_SCHEMA_VERSION` (1): u32, must be `1`.
- `DOM_QOS_TLV_KIND` (2): u32, one of the kinds above.

Client caps (CLIENT_HELLO):
- `DOM_QOS_TLV_CAPS_PERF_CLASS` (10): u32, coarse perf class (0..N).
- `DOM_QOS_TLV_CAPS_MAX_UPDATE_HZ` (11): u32, max snapshot/update cadence.
- `DOM_QOS_TLV_CAPS_MAX_DELTA_DETAIL` (12): u32, cap on detail (0..100).
- `DOM_QOS_TLV_CAPS_MAX_INTEREST_RADIUS_M` (13): u32, max interest radius in meters.

Server policy (SERVER_POLICY):
- `DOM_QOS_TLV_POLICY_UPDATE_HZ` (20): u32, snapshot/update cadence.
- `DOM_QOS_TLV_POLICY_DELTA_DETAIL` (21): u32, delta/detail scale (0..100).
- `DOM_QOS_TLV_POLICY_INTEREST_RADIUS_M` (22): u32, interest radius in meters.
- `DOM_QOS_TLV_POLICY_RECOMMENDED_PROFILE` (23): u32, perf profile hint.

Client status (CLIENT_STATUS):
- `DOM_QOS_TLV_STATUS_FPS_BUDGET` (30): u32, target frame budget (fps).
- `DOM_QOS_TLV_STATUS_BACKLOG_MS` (31): u32, backlog in milliseconds.
- `DOM_QOS_TLV_STATUS_DESIRED_REDUCTION` (32): u32, 0..3 (none..severe).
- `DOM_QOS_TLV_STATUS_FLAGS` (33): u32, diagnostic flags (optional).

## Semantics
- The server computes an effective policy by clamping server policy by client
  caps, then applying client status reductions. This affects presentation only.
- `update_hz` controls snapshot/delta cadence, not simulation tick rate.
- `delta_detail` and `interest_radius_m` affect what is sent and rendered, not
  authoritative state.
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
