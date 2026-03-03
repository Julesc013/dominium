# Electrical Constitution

Status: CANONICAL
Last Updated: 2026-03-03
Scope: ELEC-0 governance baseline for deterministic electrical/power domain integration.

## 1) Purpose

Electrical simulation is a canonical networked realism domain built from existing substrates:

- topology via `NetworkGraph`
- transport via `FlowSystem` QuantityBundles
- response laws via `ConstitutiveModels`
- protection via `SAFETY` patterns
- compliance via `SpecSheets`
- authority and mutation via `CTRL` process-only execution

No standalone bespoke "electricity engine" is permitted outside those substrates.

## 2) Power Quantities

Canonical bundle:

- `bundle.power_phasor` = `{P, Q, S}`

Notes:

- `P` (active), `Q` (reactive), and `S` (apparent) are authoritative flow components at E1+.
- `V` and `I` are derived quantities in ELEC-0 unless explicitly promoted by later series.
- Electrical losses must be represented as deterministic transforms and hooks to thermal quantity accounting (THERM series integration).

## 3) Network Topology

`PowerNetworkGraph` is a `NetworkGraph` specialization with payload identifiers for:

- buses
- generators
- loads
- storage
- breakers
- transformer links (stub)

Electrical connectivity, routing, and partition behavior must use canonical graph substrates and deterministic ordering.

## 4) Constitutive Models

Electrical response behavior is model-driven, not hardcoded:

- load demand models (resistive, motor/inductive, capacitive stubs)
- line loss models (deterministic proxy, E0/E1-appropriate)
- PF correction devices (capacitor-bank style stubs)

Model requirements:

- explicit input/output signatures
- explicit tier support
- explicit budget cost units
- deterministic cache policy

## 5) Safety Patterns

Electrical protection must be instantiated through Safety Pattern Library templates:

- `breaker` trip/disconnect
- fail-safe default off
- interlocks for unsafe switching states
- redundancy/islanding policies
- lockout-tagout for maintenance
- thermal runaway as hazard hook

Protection logic implemented outside SAFETY patterns is non-compliant.

## 6) SpecSheets And Interfaces

Electrical interfaces and compliance are data-defined through `SPEC`:

- voltage ratings
- current ratings
- connector types
- grounding class

Compliance checks:

- deterministic
- inspectable
- refusal/warn outcomes explicit
- process-driven and replayable

## 7) Tiering And Budgets

Tier contract:

- `E0` macro: global bookkeeping, active power-first simplification, coarse losses
- `E1` meso: phasor approximation (`P/Q/S`, PF)
- `E2` micro: waveform-level lab mode only, ROI constrained and optional

Budget contract:

- E0 always available baseline
- E1 activated per network and budget envelope
- E2 requires explicit fidelity arbitration and ROI approval

All degradations must be deterministic and logged.

## 8) UX And Epistemics

Diegetic observability requires instruments:

- voltmeter
- ammeter
- test lamp/continuity indicator
- breaker panel state indicators

Inspection/admin snapshots may expose wider summaries, but diegetic subjects must not receive omniscient power-map truth without entitlement/instrument pathways.

## 9) Non-Goals (ELEC-0)

- no full power-flow solver implementation
- no waveform simulation implementation
- no new ontology primitives
- no wall-clock or nondeterministic behavior

