# Signal Model (SIGNAL0)

Status: binding. Scope: signal fields, interfaces, and computation constraints.

## Purpose

Signals are first-class, data-defined fields used to express analog, digital,
mechanical, optical, RF, and symbolic computation without continuous micro-time
simulation. Signals evolve only through Processes.

## Canonical schemas

- `schema/signal.field.schema`
- `schema/signal.interface.schema`

## Core rules (non-negotiable)

- All signals are discretely sampled.
- Signal values are bounded and unit-annotated.
- All signal evolution occurs via Process execution (PROC0).
- No continuous-time integration, SPICE simulation, or per-nanosecond ticking.
- Determinism is required; randomness uses named RNG streams only.

## Signal field model

Signal fields are declarative records with:

- signal identity and type (digital / analog / symbolic / rf / optical / mechanical)
- unit annotation
- value representation (boolean / integer / fixed / vector / symbol_stream)
- bandwidth and sampling policy
- noise and latency profiles by reference (data-only)

## Signal interfaces

Signals flow through explicit interfaces. Compatibility checks are deterministic
and based on declared type, directionality, capacity, and impedance class. Partial
compatibility is expressed as degradation (noise/latency envelopes), never implicit.

## Canonical signal process families (reserved)

The following process families are reserved names and canonical IDs. Implementations
are data-only and parameterized:

- `org.dominium.process.signal.sample`
- `org.dominium.process.signal.route`
- `org.dominium.process.signal.threshold`
- `org.dominium.process.signal.filter`
- `org.dominium.process.signal.integrate`
- `org.dominium.process.signal.modulate`
- `org.dominium.process.signal.demodulate`
- `org.dominium.process.signal.quantize`
- `org.dominium.process.signal.record`
- `org.dominium.process.signal.compare`
- `org.dominium.process.signal.encrypt`
- `org.dominium.process.signal.decrypt`

## Digital logic (symbolic)

Digital logic uses symbolic signals with explicit propagation delay. Clocks are
periodic signal processes. There is no implicit global clock and no per-cycle
micro-simulation.

## Analog & mechanical computation

Analog and mechanical signals are bounded, sampled, and expressed via discrete
processes (integration, filtering, saturation, drift). Mechanical signals are
modeled as position, velocity, force, and torque fields with explicit units.

## Mixed-signal bridges

Bridges are explicit processes (ADC/DAC/relay/camera/microphone/antenna). Every
bridge introduces quantization error and latency, governed by data and standards.

## Networks & surveillance

Signal routing is explicit, bandwidth/latency constrained, and always a process.
Interception, spoofing, and jamming are data-driven processes requiring authority.

## Collapse / expand for signal domains

Signal-heavy domains MUST collapse safely. Macro capsules store:

- invariant totals (duty cycles, average load)
- distributions (noise envelopes)
- effective parameters (throughput, error rates)
- RNG stream cursors

Expand reconstructs plausible microstate and resumes RNG streams exactly.

## See also

- `docs/architecture/PROCESS_ONLY_MUTATION.md`
- `docs/architecture/DETERMINISTIC_ORDERING_POLICY.md`
- `docs/architecture/RNG_MODEL.md`
- `docs/architecture/FLOAT_POLICY.md`
- `docs/architecture/COLLAPSE_EXPAND_CONTRACT.md`
