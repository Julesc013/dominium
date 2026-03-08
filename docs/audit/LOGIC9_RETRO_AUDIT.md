## LOGIC9 Retro Audit

Date: 2026-03-08
Scope: LOGIC-9 distributed protocol layer

### Existing protocol-like concepts

- `SIG`
  - `src/signals/transport/transport_engine.py` already provides deterministic envelope creation, queueing, delivery events, knowledge receipts, routing, loss, and trust-weighted receipt handling.
  - `carrier.sig` in LOGIC-1 already maps SIG receipts into `signal.message` payloads through `sig_receipt_to_signal_request(...)`.
  - Result: LOGIC-9 must delegate long-distance or cross-shard message transport into SIG instead of introducing a second transport runtime.

- `MOB`
  - MOB signal/interlocking logic is state-machine based and remains domain-specific. It is not a generic framing/arbitration substrate.
  - Result: MOB remains an integration consumer of LOGIC/SIG protocol surfaces, not a duplicated protocol engine.

- Existing LOGIC hooks
  - `schema/logic/protocol_definition.schema` and `data/registries/protocol_registry.json` exist as LOGIC-1 stubs.
  - `src/logic/eval/propagate_engine.py` already preserves `protocol_id` and `bus_id` metadata through pending signal propagation, but does not yet frame, arbitrate, or route protocol traffic.
  - `src/logic/debug/debug_engine.py` already exposes `measure.logic.protocol_frame` as a stub summary surface.

### Duplication check

- No existing subsystem already implements:
  - deterministic frame construction in LOGIC
  - protocol-bus arbitration tied to LOGIC network edges
  - protocol event records for LOGIC propagation
- Existing SIG message transport is authoritative for message-carried delivery and should be reused, not copied.

### Minimum protocol features required

- Framing
  - deterministic header/address/payload/checksum materialization
- Arbitration
  - deterministic fixed-priority, time-slice, and token-passing selection
- Addressing
  - unicast, multicast, and broadcast within bus scope

### Integration points

- `LOGIC-4 PROPAGATE`
  - protocol framing/arbitration belongs here as the outbound delivery phase for `edge_kind == protocol_link`
- `SIG`
  - `carrier.sig` protocol delivery must flow through SIG envelopes, queue rows, delivery events, and receipts
- `LOGIC-7`
  - `measure.logic.protocol_frame` becomes a real framed-traffic observation path
- `LOGIC-8`
  - protocol links already have security policy seams and noise/fault hooks; LOGIC-9 must enforce them on framed delivery
- Shards
  - cross-shard protocol transport must stay on `carrier.sig` or boundary-artifact exchange

### Naming / glossary conflicts

- No hard conflict found with canon glossary reserved words.
- `bus`, `frame`, `endpoint`, `protocol`, `address`, `token` are already used descriptively and remain valid if kept scoped under LOGIC protocol artifacts.

### Retrofit conclusion

- Implement LOGIC-9 as:
  - a LOGIC protocol runtime layered on `protocol_link`
  - deterministic frame/arbitration state stored in LOGIC eval state
  - SIG-backed transport only for `carrier.sig`
- Do not create:
  - a separate generic network stack
  - direct protocol delivery bypassing SIG receipts for message-carried transport
