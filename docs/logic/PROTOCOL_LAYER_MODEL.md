## LOGIC Protocol Layer Model

### Purpose

LOGIC-9 makes `ProtocolDefinition` operational for deterministic distributed control. It adds framing, arbitration, addressing, and protocol event records without introducing a full routing stack or substrate bias.

### A) Protocol Roles

- `endpoint`
  - a protocol-capable logic node that sends or receives framed traffic
- `bus`
  - a deterministic shared medium or point-to-point carrier path scoped by `bus_id`
- `frame`
  - a structured payload emitted onto a protocol bus and delivered according to arbitration, delay, and security policy

### B) Framing

Protocol framing is deterministic and canonical. A frame is constructed from:

- header
- address
- payload
- checksum stub

Required properties:

- canonical field ordering
- stable `frame_id`
- deterministic checksum generation
- no hidden carrier-specific semantics in the frame format

### C) Addressing Modes

- `unicast`
  - targets a single endpoint id
- `multicast`
  - targets a declared group id or inline endpoint set
- `broadcast`
  - targets all protocol endpoints within the bus scope

Addressing affects delivery scope, not the underlying logic semantics.

### D) Arbitration Policies

Arbitration is deterministic and replay-safe.

- `arb.fixed_priority`
  - lower stable endpoint id wins
- `arb.time_slice`
  - a deterministic bus-local schedule selects the winner for the current tick
- `arb.token`
  - a deterministic token-holder state machine grants the bus to one endpoint at a time

Losing contenders remain queued in bounded form and re-enter arbitration on the next eligible tick.

### E) Error Detection Stub

- `err.checksum_stub`
  - frame checksum is computed deterministically from canonical frame content
- `err.none`
  - no checksum field is required

Corruption itself comes from LOGIC-8 noise/fault policy, not from protocol semantics. Protocol runtime only records the corruption outcome and refuses or marks delivery accordingly.

### F) Security

Protocol security delegates to SIG/LOGIC-8 policy surfaces.

- `security_policy_id` may require:
  - credential verification
  - signature verification
  - encryption policy presence
- verification failure:
  - blocks frame delivery
  - records a protocol event
  - emits explain artifacts

### Runtime rules

- Protocol links operate only through LOGIC network topology.
- `carrier.sig` deliveries must route through SIG envelopes, queue rows, delivery events, and receipts.
- No direct frame delivery bypass is allowed.
- Cross-shard protocol traffic must use `carrier.sig` or explicit boundary artifacts.

### Determinism and budgeting

- frame construction, arbitration ordering, queue progression, and address expansion are deterministic
- protocol work consumes compute budget
- throttle order is stable by bus, then frame, then endpoint id

### Explainability

Protocol runtime must surface:

- `explain.protocol_arbitration_loss`
- `explain.protocol_security_block`
- `explain.protocol_corruption`

### Non-goals

- full TCP/IP-style routing
- dynamic topology discovery
- best-effort nondeterministic retry behavior
- wall-clock scheduling
