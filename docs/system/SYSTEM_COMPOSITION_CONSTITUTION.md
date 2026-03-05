Status: BASELINE
Last Reviewed: 2026-03-05
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: SYS-0 constitutional definition for deterministic System composition and collapse.

# System Composition Constitution

## Purpose
Define a formal System layer for deterministic composition, collapse, and expansion of subsystem graphs without changing existing domain semantics.

## A) System Definition
A System is:

- A root Assembly node.
- A connected subgraph of Assemblies.
- Declared with:
  - `InterfaceSignature`
  - `TierContract`
  - `CouplingContracts`
  - `SafetyContracts`

System behavior remains model-driven and process-mediated.

## B) InterfaceSignature
Every System interface must declare:

- Boundary port definitions (port types + quantity bundles).
- Signal channels.
- Spec/rating limits.
- Exposed boundary quantities.

InterfaceSignature is authoritative for collapse eligibility and macro boundary execution.

## C) Boundary Invariants
Every System must declare invariant checks at the boundary:

- Mass conservation across boundary.
- Energy conservation across boundary (per active physics profile).
- Momentum conservation where relevant.
- Pollutant emission accounting across boundary.
- Safety fail-safe default behavior.

Invariant checks are deterministic and tolerance-governed.

## D) MacroCapsule
A MacroCapsule is a deterministic abstraction artifact containing:

- Interface signature reference.
- Boundary invariant set reference.
- Macro model bindings reference.
- Internal state vector (minimal sufficient deterministic state).
- Provenance hash anchor.

When active, capsule boundary behavior replaces internal micro/meso simulation.

## E) Collapse Eligibility
`process.system_collapse` may execute only when all checks pass:

- No unresolved hazards inside system scope.
- No pending internal scheduled events.
- No open branch dependency.
- Internal state captured into a deterministic state vector.

Failure to satisfy eligibility results in explicit refusal.

## F) Expand Operation
`process.system_expand` must:

1. Restore internal graph from serialized internal state.
2. Validate restored state hash against stored provenance anchor.
3. Rebind ports/signals at system boundary.
4. Refuse safely on hash mismatch or malformed state.

Expand is deterministic and reversible with respect to preserved state vector + anchor.

## G) Tier Integration
System tier transitions follow declared `TierContract` order:

- `micro -> meso -> macro` for degradation.
- Upward fidelity restoration only through explicit expand path.
- No silent tier transitions.

## Constitutional Constraints
- No new bespoke solver semantics in SYS-0.
- No wall-clock or nondeterministic state transitions.
- No hidden state influencing boundary behavior without inclusion in capsule state vector.
- No bypass of PHYS/TEMP/TOL/PROV process discipline.
