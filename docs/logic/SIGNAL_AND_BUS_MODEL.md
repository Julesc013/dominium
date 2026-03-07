Status: CANONICAL
Last Reviewed: 2026-03-08
Supersedes: none
Superseded By: none

# Signal And Bus Model (LOGIC-1)

Status: binding. Scope: typed signal values, bus structure, carrier constraints, deterministic serialization, and protocol hooks for later LOGIC series work.

## Purpose

LOGIC-1 defines the concrete signal layer used by future logic elements,
controllers, buses, and compiled logic artifacts.

This layer is substrate-agnostic:

- signal meaning comes from `signal_type_id`, typed value shape, and declared policy
- carrier identity contributes latency, access, and cost constraints
- future transducers bridge between physical systems and logic signals

LOGIC-1 does not implement logic element behavior, network propagation, or a
protocol runtime.

## A) Signal Core

Canonical signal records follow this shape:

```text
signal = {
  signal_id,
  signal_type_id,
  carrier_type_id,
  value,
  valid_from_tick,
  valid_until_tick?,
  metadata
}
```

Canonical time reference is the canonical tick.

- validity is tick-scoped
- latency is expressed by delay policy and schedule policy
- no wall-clock field is allowed

Authoritative mutation is process-only:

- `process.signal_set`
- `process.signal_emit_pulse`

## B) Signal Value Representations

### `signal.boolean`
- values are `0` or `1`
- canonical use: discrete enable/disable, asserted/not-asserted, open/closed

### `signal.scalar`
- value is deterministic fixed-point
- allowed uses:
  - normalized `0..1`
  - declared unit-bearing scalar through explicit metadata
- scalar semantics remain signal-side, not carrier-side

### `signal.pulse`
- value is a bounded ordered list of edge events within a declared tick window
- each edge event carries:
  - `tick_offset`
  - `edge_kind`
- this is not an unbounded event stream

### `signal.message`
- value references a SIG artifact and optional receipt metadata
- transport, trust, addressing, and encryption remain SIG-owned concerns

### `signal.bus`
- value is either:
  - ordered array of typed sub-signals, or
  - packed fixed-width scalar interpreted through a bus definition
- bus meaning comes from declared encoding and field schema, never from a carrier shortcut

## C) Bus Encodings

Bus encodings are registry-driven.

Baseline encodings:

- `encoding.bits`
  - ordered bit vector
- `encoding.uint`
  - fixed-width unsigned packed value
- `encoding.struct`
  - ordered named fields
- `encoding.frame`
  - fielded frame with protocol-oriented headers and payload slices

Bus definitions declare:

- `bus_id`
- `encoding_id`
- optional width
- optional field list
- deterministic fingerprint

## D) Carrier Constraints

Carrier declarations are non-semantic.

They may define:

- default delay policy
- default noise policy
- domain cost hooks
- access policy class
- declared transducer requirements

Carrier identity does not change the meaning of a signal value.

Examples:

- `carrier.electrical`
- `carrier.pneumatic`
- `carrier.hydraulic`
- `carrier.mechanical`
- `carrier.optical`
- `carrier.sig`

## E) Delay And Validity

Delay and validity remain TEMP-compatible.

- `valid_from_tick` and `valid_until_tick` define when a signal value is authoritative
- delay policies control when downstream consumers may observe a new value
- there is no separate clock subsystem

Baseline delay hooks:

- `delay.none`
- `delay.fixed_ticks`
- `delay.temporal_domain`
- `delay.sig_delivery`

## F) Noise And Error Hooks

Noise policy is explicit and deterministic.

Baseline hooks:

- `noise.none`
- `noise.deterministic_quantization`
- `noise.named_rng_optional`

`noise.named_rng_optional` is only a declared hook for future policy-governed
use. LOGIC-1 does not authorize anonymous randomness.

Error and noise remain model/policy concerns. They do not alter signal meaning.

## G) Protocol Hooks

Protocol definitions exist as data contracts only.

They may declare:

- framing rules reference
- arbitration policy id
- addressing behavior reference
- error-detection policy id

Baseline protocol placeholders:

- `protocol.none`
- `protocol.simple_frame_stub`
- `protocol.bus_arbitration_stub`

LOGIC-1 does not implement bus contention, delivery, or frame execution.

## H) Deterministic Serialization

Signals, buses, and protocol definitions must serialize canonically.

Required properties:

- stable field ordering
- canonical JSON serialization
- deterministic SHA-256 fingerprinting
- stable row ordering by:
  - `network_id`
  - `element_id`
  - `port_id`
  - `tick`

These hashes are used for:

- proofs
- compilation inputs
- change detection
- replay-safe artifacts

## I) Observation And Epistemics

Signal values are not freely readable.

Reading requires:

- instrumentation surface measurement point
- instrument type
- access policy

Signal traces are derived artifacts:

- deterministic
- compactable under provenance rules
- never a direct truth leak into `RenderModel`

## J) Compute And Coupling Hooks

Bulk signal updates must request META-COMPUTE units:

- `instruction_units`
- `memory_units`

Signal change records must also produce deterministic change tokens suitable for
later COUPLE relevance scheduling.

Tolerance-aware change detection is required before a signal delta is treated as
material for coupling evaluation.

## Non-Goals

- no gates, relays, latches, timers, or PLC elements
- no full network propagation engine
- no protocol execution runtime
- no direct carrier physics inside LOGIC
