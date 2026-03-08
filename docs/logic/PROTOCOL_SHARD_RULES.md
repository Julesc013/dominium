# Protocol Shard Rules

Status: normative
Version: 1.0.0
Scope: LOGIC-9 protocol buses and framed traffic

## Purpose

Protocol traffic may cross shard boundaries, but only through explicit asynchronous exchange seams.

This document narrows the LOGIC-3 shard rule for protocol buses:

- no direct same-tick cross-shard protocol delivery
- SIG-backed or boundary-artifact exchange only
- deterministic merge and arbitration order at the receiving side

## Rules

### 1. No direct synchronous cross-shard protocol delivery

- `edge.protocol_link` must not deliver directly across shards in the same canonical tick.
- A protocol frame that leaves one shard must re-enter another shard through an asynchronous transport seam.

## 2. Allowed boundary forms

- `carrier.sig` backed protocol transport
- explicit boundary artifact exchange declared on the edge or endpoint extensions

Accepted boundary markers:

- `boundary_artifact_id`
- `boundary_artifact_exchange = true`

## 3. Boundary nodes are mandatory

If a protocol bus spans shards, the topology must declare boundary-safe endpoints or artifact seams.

- direct `protocol_link` across different `extensions.shard_id` values is invalid unless boundary-safe
- `sig_link` remains valid because SIG owns the asynchronous delivery contract

## 4. Deterministic merge order

When frames arrive from shard boundaries:

- arbitration still runs in canonical policy order
- frame ordering is stabilized by `(tick_sent, src_endpoint_id, frame_id)`
- boundary artifacts must not introduce hidden priority

## 5. SIG-backed transport

For `carrier.sig` protocol links:

- frames are transported as SIG artifacts
- delivery visibility follows SIG receipts and delivery events
- trust, encryption, and authorization remain SIG-owned
- protocol delivery must not bypass SIG receipts

## 6. Debugging and replay

- protocol sniffers may observe framed traffic only through instrumentation surfaces and lawful access
- boundary traffic remains replay-safe and compactable
- proof surfaces must retain protocol frame, arbitration, and protocol event hash chains

## Non-Goals

- no shard router implementation
- no same-tick multi-shard bus solve
- no hidden global bus clock
