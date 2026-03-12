Status: DERIVED
Version: 1.0.0
Last Reviewed: 2026-03-01
Scope: CTRL-10 retro-consistency audit for final control-plane envelope
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# CTRL10 Retro Audit

## Canon/Invariant Frame
- `docs/canon/constitution_v1.md`: A1, A2, A3, A4, A7, A10.
- `docs/canon/glossary_v1.md`: AuthorityContext, Determinism, Refusal, Capability, Epistemic Scope.
- `AGENTS.md`: process-only mutation, no runtime mode flags, deterministic ordering.
- CTRL-10 target checks:
  - all interaction paths route through `ControlPlane`
  - all downgrades are decision-log visible
  - no direct RS-5 envelope usage outside control negotiation/fidelity kernels
  - all temporary effect modifications route through effect system processes
  - no legacy/quarantine control logic linked from production/runtime paths

## Audit Method
- Interaction gateway scan:
  - `rg -n "build_control_intent\(|build_control_resolution\(" src tools -g "*.py"`
  - `rg -n "build_client_intent_envelope\(|_build_envelope\(" src tools -g "*.py"`
- Downgrade and decision-log linkage scan:
  - `rg -n "downgrade_entries|downgrade_reasons|decision_log_ref|run_meta/control_decisions" src/control tools -g "*.py"`
- RS-5 envelope usage scan:
  - `rg -n "rs5_budget_state|max_cost_units_per_tick|arbitrate_fidelity_requests|negotiate_request" src tools -g "*.py"`
- Effect mutation path scan:
  - `rg -n "process.effect_apply|process.effect_remove|temporary_|temp_|interior_movement_constraints" src tools -g "*.py"`
- Legacy/quarantine contamination scan:
  - `rg -n "legacy/|quarantine/" src tools -g "*.py"`

## Findings

### F1 - Interaction path routing
- Public interaction entrypoints remain control-routed:
  - `src/client/interaction/interaction_dispatch.py` builds `ControlIntent` and resolves through control plane.
  - No new public UI path directly dispatching `process.*` found.
- Network adapters (`src/net/policies/policy_server_authoritative.py`, `src/net/srz/shard_coordinator.py`) still construct transport envelopes as policy/runtime boundary code.
- Assessment: compliant with control gateway architecture; adapter exception remains explicit.

### F2 - Downgrade logging
- `src/control/control_plane_engine.py` records downgrade entries/reasons and writes deterministic decision logs to `run_meta/control_decisions/*`.
- `control_ir` mapping continues to preserve `decision_log_ref` and downgrade reason propagation.
- Assessment: compliant; no silent downgrade path detected in control resolution path.

### F3 - RS-5 envelope isolation
- RS-5 budget envelope references are located in control negotiation/fidelity and domain-level fidelity request call sites.
- No direct domain-local downgrade branching detected bypassing control negotiation.
- Assessment: compliant with existing CTRL architecture; RS-5 mechanics remain deterministic and explicit.

### F4 - Effect mutation isolation
- Effect state writes remain process-gated via:
  - `process.effect_apply`
  - `process.effect_remove`
  - deterministic pruning/query in `src/control/effects/effect_engine.py`
- No ad hoc temporary control flags reintroduced in runtime paths.
- Assessment: compliant.

### F5 - Legacy/quarantine control logic
- No production/runtime imports of `legacy/` or `quarantine/` detected in control plane/runtime paths.
- Existing governance/analyzer tooling for deprecated/quarantine references remains active.
- Assessment: compliant.

## Remaining Violations
- No hard violations found in this audit pass for CTRL-10 entry criteria.

## Required Deprecation Entries
- None required from this pass.

## Hardening Follow-ups for CTRL-10
1. Add control proof bundle artifact integration and include deterministic control decision hashes in lockstep composite anchors.
2. Add full control-plane regression lock artifact with explicit update-tag gate.
3. Extend RepoX with domain control registration enforcement for future user-facing process families.
