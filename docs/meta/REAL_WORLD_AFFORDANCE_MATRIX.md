# Real-World Affordance Matrix

Status: CANONICAL
Last Updated: 2026-03-03
Scope: COMPLETENESS-1 governance substrate for affordance coverage.

## 1) Purpose

The Real-World Affordance Matrix (RWAM) is the canonical completeness contract for domain growth.
It replaces ad-hoc scope checks with a deterministic matrix that maps real-world affordance classes to existing substrates and series coverage.

RWAM constraints:

- every new series must declare which canonical affordances it touches
- every declaration must name substrates and macro/meso/micro tier behavior
- missing coverage is explicit (planned) instead of silent drift
- enforcement is governance-only; runtime behavior is unchanged

## 2) Canonical Affordance Categories

### A) Matter/Energy Transformation

Representative actions:

- cut/drill/weld/mix/burn/explode/refine/phase change

Current substrate coverage:

- MAT
- MECH
- SPEC
- META-ACTION-0 (TRANSFORM family)

Series coverage:

- implemented: MAT, MECH, SPEC
- planned: DOM, ELEC, SCI

Known gaps:

- no dedicated chemistry/electrochem transform solver yet
- no full biological metabolism substrate yet

### B) Motion And Force Transmission

Representative actions:

- push/pull/lift/gear/rope/couple/steer/brake/orbit

Current substrate coverage:

- MOB
- MECH
- ABS (constraints/state/schedule)
- FIELD

Series coverage:

- implemented: MOB, MECH, FIELD
- planned: ADV

Known gaps:

- high-fidelity orbital and advanced propulsion are not yet implemented

### C) Containment And Interfaces

Representative actions:

- seal/pressurize/vent/connector/standard compatibility

Current substrate coverage:

- INT
- ACT (ports/tools/surfaces)
- SPEC
- ABS Flow/Hazard

Series coverage:

- implemented: INT, ACT, SPEC
- planned: ELEC, DOM

Known gaps:

- full machine HVAC/electrical connector simulation remains future work

### D) Measurement And Verification

Representative actions:

- observe/sample/calibrate/inspect/certify

Current substrate coverage:

- META-INFO-0
- CTRL (inspection/decision/proof)
- SPEC compliance checks
- ACT sensing/instrument surfaces

Series coverage:

- implemented: SPEC, SIG, MOB, MAT
- planned: SCI

Known gaps:

- advanced scientific instrumentation families are not yet specialized

### E) Communication And Coordination

Representative actions:

- send/broadcast/relay/encrypt/jam/trust

Current substrate coverage:

- SIG
- META-INFO-0
- CTRL
- ABS NetworkGraph/Flow
- FIELD attenuation hooks

Series coverage:

- implemented: SIG
- planned: MIL, ECO, SCI

Known gaps:

- domain-specific comm doctrine (military/economic/scientific) is not yet layered

### F) Institutions And Contracts

Representative actions:

- allocate/approve/standardize/enforce/insure/procure

Current substrate coverage:

- CTRL
- SPEC
- SIG institutional comms
- MAT commitments/provenance

Series coverage:

- implemented: SIG, SPEC, MAT
- planned: ECO, CIV expansion

Known gaps:

- insurance/procurement market logic is not yet implemented

### G) Environment And Living Systems

Representative actions:

- weather/fluid/geology/biology/decay/disease

Current substrate coverage:

- FIELD
- INT flows
- MAT maintenance/decay hooks
- MECH stress/degradation hooks

Series coverage:

- implemented: FIELD (baseline), MAT (wear hooks)
- planned: DOM, BIO

Known gaps:

- full living systems and disease ecology are future domain work

### H) Time And Synchronization

Representative actions:

- clocks/schedules/drift/timestamp/traceability

Current substrate coverage:

- RS time/budget/tier governance
- ABS ScheduleComponent
- MAT provenance and event streams
- CTRL decision logs/proof bundles

Series coverage:

- implemented: RS, ABS, MAT, CTRL
- planned: ECO, SCI

Known gaps:

- no external wall-clock authoritative semantics (by design)

### I) Safety And Protection

Representative actions:

- interlocks/relief/breakers/redundancy/fail-safe

Current substrate coverage:

- MOB signaling/interlocking
- MECH failure/thresholds
- MAT maintenance hazards
- CTRL effects/refusals/policy gates

Series coverage:

- implemented: MOB, MECH, MAT, CTRL
- planned: ELEC, LOGIC, MIL

Known gaps:

- generalized power-protection and automation interlock domains are future work

## 3) Governance Rules

Mandatory:

- every new series must update `data/meta/real_world_affordance_matrix.json`
- every new series must map to at least one canonical affordance
- every declared affordance mapping must list substrates, tiers, determinism, and replay/proof impact
- no new ontology primitive can bypass matrix declaration

Constitutive response mapping:

- realism-detail response logic (thresholds, response curves, attenuation laws, wear response) is governed by `META-MODEL`
- new realism details must map through registered constitutive models, not bespoke inline domain logic
- RWAM machine mappings must include `META_MODEL` affordance coverage declarations where those details are touched

ELEC-0 domain declaration:

- `ELEC` explicitly maps to:
  - `matter_transformation` (fuel/drive conversion to electrical power context)
  - `containment_interfaces` (connector and rating interfaces)
  - `measurement_verification` (instrument/compliance inspection)
  - `communication_coordination` (dispatch/reporting and SIG integration)
  - `safety_protection` (breaker/fail-safe/interlock/LOTO patterns)
- electrical tier declaration:
  - macro (`E0`) bookkeeping baseline
  - meso (`E1`) phasor approximation
  - micro (`E2`) ROI-limited waveform lab tier (optional)

## 4) Non-Goals

- no runtime behavior changes
- no simulation semantic changes
- no nondeterministic governance behavior
- no optional-pack boot dependencies
