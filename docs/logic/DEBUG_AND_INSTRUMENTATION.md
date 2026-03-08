# LOGIC Debugging And Instrumentation

## Scope

LOGIC-7 defines bounded, deterministic, epistemically constrained debugging for logic signals, buses, compiled controllers, and protocol views. It does not grant omniscient access and it does not bypass META-INSTR, META-COMPUTE, PROV, TEMP, or SYS.

## Instruments

### `instrument.logic_probe`

- Reads one measurement point at a time.
- The logic probe is the single-point diegetic instrument for signal inspection.
- Intended for direct signal/port inspection.
- Uses instrumentation surfaces and access policies.
- Does not expose hidden state unless the target measurement point explicitly permits it.

### `instrument.logic_analyzer`

- Records bounded traces over a declared tick window.
- The logic analyzer is the bounded trace capture instrument.
- Samples only declared measurement points.
- Sampling rate and span are capped by policy.
- The analyzer always operates at a bounded sampling rate.
- Throttling is deterministic and explainable.

### `instrument.protocol_sniffer_stub`

- The protocol sniffer stub is the local framed-bus inspection instrument.
- Interprets local bus/frame payloads through `protocol_definition`.
- Produces a derived frame summary only.
- Does not implement a transport stack or remote protocol execution.

## Epistemic Access

### Physical Access

- Local probing requires physical access when the instrumentation surface demands it.
- Cabinet, panel, or wired access remains a domain/policy concern; LOGIC only consumes the access result.

### Authority Access

- Remote monitoring requires entitlements and a permitted access policy.
- Message-carrier observation uses SIG-mediated authorization, not direct truth reads.

### Ranked Policy

- Ranked profiles may forbid:
  - analyzer sessions
  - remote protocol sniffing
  - debug-driven force expand

## Trace Model

- Trace artifacts are derived.
- Trace artifacts are compactable.
- Trace capture is bounded by:
  - `max_points`
  - `max_ticks`
  - `max_samples`
- Trace capture always has a bounded length.
- Sampling is deterministic under budget pressure.
- If a controller remains compiled/collapsed, default trace scope is boundary I/O only.

## Observer Effect

- Debugging may be observer-expensive.
- Internal inspection of a compiled/collapsed controller may force expand to L1.
- Force expand is policy-gated, budgeted, and logged.
- If expand is not permitted, the request is refused explicitly.

## Deterministic Sampling

- Trace sessions sort measurement points deterministically.
- Sample windows are evaluated on canonical tick boundaries only.
- Under budget pressure, the active sampling policy selects one of:
  - `deterministic_subsample`
  - `reduce_points`
  - `refuse`
- No wall-clock timers are valid.

## Compiled / Collapsed Controllers

- Default observation on compiled/collapsed controllers:
  - boundary inputs
  - boundary outputs
  - compiled summary
  - bounded truth-table excerpts for eligible combinational modules
- Internal nodes, internal edges, and state-vector inspection require forced expand or refusal.

## Trace Classification

- Trace artifacts are derived and compactable.
- Debug requests may be recorded canonically in stricter profiles for auditability.
- Policy decides request classification; trace payloads remain derived.

## Explain Contracts

- `explain.logic_debug_refused`
- `explain.logic_debug_throttled`
- `explain.logic_debug_forced_expand`

These explains cover:

- missing access or forbidden tools
- budget-driven trace throttling
- forced expand requests or forced expand denial paths

## Non-Goals

- No direct Truth readout path to RenderModel.
- No unbounded history capture.
- No protocol stack implementation.
- No wall-clock timing.
