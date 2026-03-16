Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Containment And Failure

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Status: CANONICAL
Last Updated: 2026-03-04
Scope: FLUID-2 pressure containment, burst, leak, and deterministic cascade policy.

## 1) Pressure Vessel Model

`spec.pressure_vessel` defines canonical thresholds:

- `max_pressure_head`
- `relief_threshold`
- `burst_threshold`
- `fatigue_limit` (optional)

When omitted, runtime derives deterministic fallback thresholds from vessel rating fields in node `state_ref`.

## 2) Failure Paths

### 2.1 Relief Path (Preferred Safe Path)

Trigger condition:

- computed local head > `relief_threshold`

Actions:

- trigger `safety.pressure_relief`
- vent deterministic excess mass via FlowSystem transfer event to declared sink
- emit RECORD artifacts and explain artifact (`event_kind_id = fluid.overpressure`)

### 2.2 Burst Path (Catastrophic Path)

Trigger condition:

- computed local head > `burst_threshold`

Actions:

- invoke `process.burst_event`
- create `burst_event` artifact
- mark target as ruptured and create active `leak_state`
- route ongoing mass escape via `process.leak_tick`
- emit explain artifact (`event_kind_id = fluid.burst`)

## 3) Leak Model

Gradual leak is model-driven (`model.fluid_leak_rate_stub`):

- leak flow scales with pressure differential and leak coefficient
- leak state persists until isolated/repaired
- every leak tick emits deterministic FlowSystem transfer artifacts

## 4) Cavitation Coupling

When local head is below vapor pressure proxy:

- increment `hazard.cavitation`
- optionally emit performance-degrade effect through model output
- emit explain artifact (`event_kind_id = fluid.cavitation`)

## 5) Cascade Policy

Leak/burst cascades are deterministic and bounded:

- evaluation order sorted by target id
- explicit cap on processed failure/leak targets per tick
- overflow degrades deterministically and logs decision entry

No unbounded recursive propagation is allowed.

## 6) INT Coupling

Leak flow toward interior is emitted as coupling rows:

- transferred mass (from FLUID)
- target compartment id (INT)
- hazard flood increment suggestion

INT remains the owner of interior state transitions; FLUID does not perform ad-hoc interior mutation.

## 7) Safety and MECH Hooks

Containment failures may emit:

- safety events (relief/burst disk/fail-safe)
- structural overload hazard hints
- optional impulse hook rows for MECH/PHYS integration

Direct fracture logic remains outside FLUID (MECH-owned).

## 8) Determinism and Proof

FLUID-2 proof surfaces include:

- `leak_hash_chain`
- `burst_hash_chain`
- `relief_event_hash_chain`

Replay windows must reproduce identical failure ordering and hash chains for identical inputs.
