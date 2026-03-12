Status: AUTHORITATIVE
Last Reviewed: 2026-03-08
Version: 1.0.0
Scope: LOGIC-4 deterministic L1 evaluation for validated logic networks.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Logic Evaluation Engine

## 1. Purpose

LOGIC-4 defines deterministic L1 logic evaluation for validated logic networks.

It executes the canonical phase cycle:

1. `SENSE`
2. `COMPUTE`
3. `COMMIT`
4. `PROPAGATE`

It is:
- process-mediated
- budgeted through META-COMPUTE
- constrained by LOGIC-3 validation and loop policy
- substrate-agnostic
- replay-safe

It is not:
- a protocol stack
- a compilation/collapse engine
- a wall-clock scheduler
- a direct actuator runtime

## 2. Phase Semantics

### 2.1 SENSE
- Reads only.
- Builds an immutable per-network snapshot at canonical tick `t`.
- Samples authoritative input signals whose validity window includes `t`.
- Resolves element state from explicit STATEVEC snapshots only.
- No state writes, signal writes, or derived mutation are allowed here.

### 2.2 COMPUTE
- Pure evaluation only.
- For each element, computes:
  - next outputs
  - next state
- Inputs are limited to:
  - SENSE snapshot
  - explicit prior state
  - declared timing/delay parameters
- No authoritative writes are permitted.

### 2.3 COMMIT
- Writes explicit state-vector snapshots only.
- Hidden state, caches, and direct row mutation are forbidden.
- Canonical state update records must be emitted when behavior changes truth.

### 2.4 PROPAGATE
- Schedules output changes to downstream signal slots.
- Propagation uses declared graph edges and delay policies.
- Authoritative signal mutation routes through canonical LOGIC signal process helpers.
- No intra-tick visibility is permitted; even `delay.none` becomes visible on `t + 1`.

## 3. Ordering

Canonical evaluation order is:
- networks sorted by `network_id`
- elements sorted by `element_instance_id`
- ports sorted by `port_id`
- edges traversed in deterministic graph order:
  - `(from_node_id, to_node_id, edge_id)`

If equal-priority work competes for a budgeted decision:
- owner priority resolves first
- stable lexical id resolves ties

No hash-map iteration order, pointer order, or thread completion order may affect authoritative outcomes.

## 4. Budgeting

LOGIC-4 is budget mandatory.

### 4.1 Per-element metering
- Every element evaluation requests:
  - `instruction_units`
  - `memory_units`
- Request source:
  - `compute_cost_units` from the element definition
  - explicit state-vector footprint for the instance

### 4.2 Per-network metering
- Network orchestration also consumes compute.
- Budget pressure must not silently skip unordered subsets.

### 4.3 Deterministic throttle order
- Throttle/refusal order is deterministic.
- Budget decisions are surfaced as:
  - canonical throttle events
  - explain artifacts
  - eval summary rows

Allowed outcomes:
- complete
- throttled
- deferred
- refused

## 5. Timing And Delays

Timing is derived from TEMP-compatible delay policies.

Supported propagation hooks:
- `delay.none`
  - visible next tick only
- `delay.fixed_ticks`
  - visible at `t + k`
- `delay.temporal_domain`
  - visible after TEMP mapping resolution
- `delay.sig_delivery`
  - routed through message-carrier delivery seam

There is no separate LOGIC clock subsystem.

Timer and counter elements remain deterministic because they advance from canonical tick progression and declared delay state, not wall-clock input.

## 6. Loop Handling

LOGIC-4 must consume LOGIC-3 validation output before executing a network.

### 6.1 Combinational loops
- Refused by default.
- Result:
  - refuse evaluation
  - emit `explain.logic_loop_detected`

### 6.2 Sequential loops
- Allowed.
- Evaluated through normal L1 snapshot semantics.

### 6.3 Mixed loops
- Policy-controlled.
- If policy requires ROI:
  - refuse in L1
  - mark network as requiring L2
- If policy requires compiled proof:
  - refuse unless compiled equivalence proof is present

Loop handling must be deterministic and must not downgrade silently.

## 7. State Vector Discipline

- All output-affecting state must come from explicit STATEVEC snapshots.
- Instance state is owned per `element_instance_id`.
- Definitions may be derived deterministically from pack-declared element definitions, but runtime mutation still commits through explicit snapshots only.
- No writes outside COMMIT are allowed.

## 8. Propagation Semantics

PROPAGATE traverses the validated `LogicNetworkGraph`.

- fanout is supported through deterministic reachability
- merges are resolved in stable source order
- bus/protocol topology remains topological here; full protocol execution is out of scope
- `carrier.sig` routes message payloads through the carrier adapter seam

LOGIC-4 emits:
- signal change records
- propagation trace artifacts
- coupling relevance inputs

It does not emit direct foreign-domain actuator mutation yet.

## 9. Explainability

Required explain surfaces:
- `explain.logic_compute_throttle`
- `explain.logic_timing_violation`
- `explain.logic_loop_detected`
- `explain.logic_command_refused`

Explain output must describe:
- refusal reason
- throttle reason
- delay application
- policy-gated L1 refusal

Explain artifacts are derived and compactable. They must not leak hidden truth into `RenderModel`.

## 10. Epistemics

- Signal reads exposed to players still require logic instrumentation and access policy.
- Logic analyzer traces are derived artifacts, not omniscient runtime dumps.
- Debug visibility remains governed by META-INSTR and access policy.

## 11. Proof And Replay

LOGIC-4 adds replay-relevant hash surfaces for:
- logic throttle events
- logic state update records
- logic output signal writes

Per-tick eval summaries and propagation traces are derived and compactable.

Replay verification must confirm:
- identical output signal hash chains
- identical throttle event hash chains
- identical state update hash chains

## 12. Non-Goals

- No protocol framing execution.
- No compiled/collapsed controller execution path.
- No oscillator micro-timing runtime.
- No direct process-actuator command bridge yet.

## 13. Readiness

LOGIC-4 provides the deterministic runtime needed for:
- LOGIC-5 timing and oscillation pattern analysis
- LOGIC-6 compiled/collapsed controller equivalence
- LOGIC-7 analyzer-grade debug and trace tooling
