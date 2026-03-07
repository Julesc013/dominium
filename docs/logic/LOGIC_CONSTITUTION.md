Status: CANONICAL
Last Reviewed: 2026-03-08
Supersedes: none
Superseded By: none

# Logic Constitution (LOGIC-0)

Status: binding. Scope: cybernetic control semantics, typed signals, deterministic evaluation, budgeted execution, and future-safe compilation/collapse for logic assemblies.

## Purpose

LOGIC defines discrete control behavior for Dominium as cybernetics: control,
communication, and feedback over typed signals and state transitions. LOGIC is
substrate-agnostic and does not assume electricity, pressure, motion, optics, or
any other physical carrier as its semantic base.

LOGIC-0 is constitutional only. It defines contracts, vocabulary, and
enforcement surfaces. It does not implement gates, relays, timers, PLCs, or the
full network evaluator yet.

## Binding dependencies

- `docs/architecture/SIGNAL_MODEL.md`
- `docs/meta/COMPUTE_BUDGET_CONSTITUTION.md`
- `docs/meta/COMPILED_MODEL_CONSTITUTION.md`
- `docs/audit/PROFILE_OVERRIDE_BASELINE.md`
- `docs/audit/REFERENCE_INTERPRETER_BASELINE.md`
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`

## A) Logic ontology

Logic is discrete control behavior expressed as:

- typed signals
- discrete state machines
- schedules and delays

Logic does not assume a physical carrier. Carrier behavior constrains cost,
latency, noise, safety, and observability, but it does not define the meaning of
logic.

Authoritative logic state evolves only through deterministic Process execution.
No UI, renderer, debug tool, or ad hoc script may mutate logic truth directly.

## B) Signal types

The following signal types are canonical and first-class:

- `signal.boolean`
  - low/high discrete value
- `signal.scalar`
  - fixed-point `0..1` scalar or a unit-bearing scalar by referenced value schema
- `signal.pulse`
  - edge-like event signal with explicit temporal semantics
- `signal.message`
  - reference to a SIG artifact or receipt-governed message payload
- `signal.bus`
  - typed vector or bundle of sub-signals with declared element schema

Signal payload meaning is defined by declared value schema and interface
signature, never by implicit carrier assumptions.

## C) Carrier types

Carrier types are registry-driven. Non-normative baseline examples:

- `carrier.electrical`
- `carrier.pneumatic`
- `carrier.hydraulic`
- `carrier.mechanical`
- `carrier.optical`
- `carrier.sig`

Carriers define constraints and costs:

- latency and delay classes
- noise/error envelopes
- transduction cost
- trust/receipt constraints for message carriers
- coupling cost and relevance impact

Carriers do not define logic semantics.

## D) Transducers

A transducer is a `System` with a declared interface signature:

- physical port(s) -> signal port(s)
- signal port(s) -> physical port(s)

Transducers are constitutive-model driven. Each transducer must declare:

- input interface signature
- output interface signature
- model bindings
- error-bound policy
- deterministic fingerprint

Transducers are the only canonical bridge between physical carriers and logic
signal semantics.

## E) Evaluation semantics

Default meso logic evaluation (`L1`, aligned with `meso`) executes per canonical
tick as:

1. `SENSE`
   - sample input signals into a stable snapshot
2. `COMPUTE`
   - compute next values as a pure function of:
     - sampled snapshot
     - declared internal state
     - declared policy/profile inputs
3. `COMMIT`
   - apply state updates
4. `PROPAGATE`
   - enqueue downstream signal updates with declared delay policy

Stable ordering is mandatory:

- networks sort by `network_id`
- elements sort by `element_id`
- ports sort by `port_id`

Within a phase, reads observe the stable snapshot of that phase. Writes become
authoritative only at `COMMIT`. Cross-element propagation occurs only through the
declared propagation queue and delay policy.

## F) Loops and oscillation

Combinational loops are forbidden by default.

Loop detection must be deterministic:

- based on declared graph topology
- evaluated in stable ID order
- profile/policy resolved before execution

If a loop is detected:

- default: refuse evaluation
- optional: force ROI micro timing if policy explicitly allows it
- optional: allow only under capped/declared policy if future profiles prove it

Oscillation is not silent. It must emit explain artifacts with enough input and
policy context to reproduce the refusal, throttle, or forced expand decision.

## G) Tiering

LOGIC tiers align to canonical tier language as:

- `L0` macro
  - compiled/capsule controller execution
- `L1` meso
  - network evaluation using `SENSE -> COMPUTE -> COMMIT -> PROPAGATE`
- `L2` micro ROI
  - timing detail, bounce, jitter, and trace-heavy inspection

Tier transitions follow SYS tier policy:

- budgeted
- deterministic
- explainable
- process-governed

Default deterministic degradation order is:

- `L2 -> L1 -> L0`

No hidden fallback between tiers is allowed.

## H) Compute budgeting

Every logic evaluation must consume:

- `instruction_units`
- `memory_units`

Compute consumption must route through META-COMPUTE. Over-budget behavior is
deterministic and policy driven:

- throttle
- degrade
- refuse

Compiled logic must declare:

- compute cost model
- memory footprint estimate
- validity domain
- equivalence proof path

LOGIC may not introduce free-running evaluators, implicit clocks, or unmetered
micro-loops.

## I) Security and epistemics

Reading logic signals is not omniscient.

Logic debugging requires:

- instrumentation surfaces
- appropriate access policy
- diegetic instrument availability

Future baseline instruments are already reserved:

- `instrument.logic_probe`
- `instrument.logic_analyzer`

Message-carrier logic must obey SIG trust, encryption, and receipt policies.
Traces are derived artifacts, not truth leaks, and may be compacted only under
provenance rules.

Truth must not leak into `RenderModel` through logic debug or explain paths.

## J) Rule-breaking

Any rule override must be:

- profile-controlled
- exception-logged
- replayable
- proofable

Examples include:

- allowing otherwise forbidden loops
- forcing extreme timing resolution
- suppressing default refusal behavior

No mode flags are allowed. Overrides must resolve through profile policy and
emit canonical exception-event artifacts.

## K) Explainability

LOGIC decisions that alter fidelity, timing, acceptance, or refusal must be
explainable through declared explain contracts.

Standard explain event kinds:

- `explain.logic_loop_detected`
- `explain.logic_oscillation`
- `explain.logic_timing_violation`
- `explain.logic_compute_throttle`
- `explain.logic_command_refused`

Explain artifacts must remain derived-only and deterministic. They must never
mutate authoritative logic truth.

## Timing model

LOGIC has no implicit global clock subsystem.

Timing emerges from:

- TEMP canonical tick
- declared schedules
- propagation delay policy
- ROI micro timing when explicitly required

Periodic behavior is modeled as declared signal/process scheduling, consistent
with `docs/architecture/SIGNAL_MODEL.md`. Global wall-clock dependencies are
forbidden.

## Coupling and actuation

Logic does not write directly into foreign domains. Canonical couplings are:

- logic -> actuator command via Process
- logic <- sensor/transducer via model-driven signal generation
- logic <- SIG message via receipt-governed message carrier

Direct foreign-domain mutation from logic assemblies is forbidden.

## Compilation and collapse

LOGIC must converge on the existing COMPILE and SYS pathways, not a bespoke
compiler or capsule runtime.

Future compiled logic may target:

- automata
- transition tables
- deterministic IR

Compilation must use COMPILE-0 proof/equivalence discipline.

Collapsed controllers must use SYS collapse/expand discipline:

- explicit validity domain
- bounded error
- forced expand on edge conditions
- deterministic hash/replay behavior

## Non-goals for LOGIC-0

- No specific gate, relay, latch, timer, or PLC implementation yet.
- No full logic network runtime yet.
- No carrier-specific solver implementation yet.
- No wall-clock scheduling subsystem.
- No truth leak into renderer/debug presentation.

## Enforcement intent

RepoX, AuditX, and TestX must reject:

- electrical bias in logic semantics
- unmetered logic compute
- omniscient logic debug
- rule-breaking outside profile and exception-event pathways

LOGIC-1 and LOGIC-2 may build on this constitution, but may not weaken it.
