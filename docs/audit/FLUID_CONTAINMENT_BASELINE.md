# FLUID Containment Baseline

Status: BASELINE
Last Updated: 2026-03-04
Scope: FLUID-2 containment, overpressure, burst, leaks, and interior coupling.

## 1) Pressure Vessel Model

Implemented deterministic vessel-state substrate:

- `pressure_vessel_state` schema + JSON schema
- vessel thresholds resolved from node `state_ref` (`relief_threshold`, `burst_threshold`, rating fallback)
- per-tick vessel state snapshots emitted as `pressure_vessel_state_rows`

## 2) Relief / Burst Logic

Runtime path in `src/fluid/network/fluid_network_engine.py` now supports:

- overpressure relief via `safety.relief_pressure`
- vented mass transfer via FlowSystem transfer events
- burst escalation via `process.burst_event` helper
- burst safety event via `safety.burst_disk`

Deterministic ordering is preserved by sorted node/target iteration and bounded failure caps.

## 3) Leak Substrate and Processes

Added deterministic process helpers:

- `process_start_leak` (`build_leak_state`)
- `process_leak_tick` (mass transfer + hazard/coupling emission)
- `process_burst_event` (burst artifact + leak bootstrap)

Artifacts and states:

- `leak_state_rows`
- `burst_event_rows`
- `leak_event_rows`
- `flow_transfer_events`

## 4) INT Coupling

Leaks targeting interior sinks emit explicit coupling rows:

- `interior_coupling_rows`
- transferred mass and flood-hazard increment hints

FLUID emits coupling artifacts only; INT remains owner of compartment state transitions.

## 5) Safety + MECH Coupling Hooks

Burst path now emits:

- `hazard.structural_overload` hint rows
- `mech_coupling_rows` with optional impulse-hook payload (`process.apply_impulse` contract hint)

No direct fracture logic was added in FLUID.

## 6) Explain Artifacts

Explain artifacts are generated deterministically for:

- `fluid.overpressure`
- `fluid.burst`
- `fluid.leak`
- `fluid.cavitation`

Generation uses explain contracts + decision/safety/hazard/model evidence and produces `explain_artifact_rows`.

## 7) Proof and Replay Surfaces

Extended proof bundle surfaces with deterministic hash chains:

- `leak_hash_chain`
- `burst_hash_chain`
- `relief_event_hash_chain`

Control proof builder, proof schema docs, and net proof-surface propagation were updated accordingly.

## 8) Governance Enforcement

RepoX:

- added `INV-FLUID-FAILURE-THROUGH-SAFETY-OR-PROCESS`
- added `INV-NO-DIRECT-MASS-MUTATION`
- added corresponding rule entries and scan logic

AuditX:

- added `E221_INLINE_BURST_LOGIC_SMELL`
- added `E222_DIRECT_INTERIOR_MASS_WRITE_SMELL`

## 9) TestX Coverage

Added FLUID-2 tests:

1. `test_relief_prevents_burst_when_thresholds_allow`
2. `test_burst_event_deterministic`
3. `test_leak_mass_transfer_logged`
4. `test_flooding_updates_int_compartment`
5. `test_cascade_bounded`
6. `test_proof_hash_stable`

## 10) Readiness

FLUID-2 baseline now provides deterministic containment/failure substrate suitable for FLUID-3 scale/stress follow-up.

## 11) Gate Execution Snapshot (2026-03-04)

- `RepoX STRICT`: PASS (`python tools/xstack/repox/check.py --profile STRICT`)
- `AuditX STRICT`: RUN COMPLETE (`findings_count=1648`, includes global pre-existing promoted blockers)
- `TestX STRICT` (FLUID-2 subset): PASS
  - `test_relief_prevents_burst_when_thresholds_allow`
  - `test_burst_event_deterministic`
  - `test_leak_mass_transfer_logged`
  - `test_flooding_updates_int_compartment`
  - `test_cascade_bounded`
  - `test_proof_hash_stable`
- `Strict build`: REFUSAL at orchestration layer due pre-existing global baseline issues outside FLUID-2
  - `compatx` refusals (project-wide)
  - `session_boot.smoke` refusal
  - `auditx` promoted blockers
  - `testx` global suite failures
  - `packaging.verify` refusal
- `Topology map`: refreshed
  - `docs/audit/TOPOLOGY_MAP.json`
  - `docs/audit/TOPOLOGY_MAP.md`
