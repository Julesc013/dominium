Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Electrical UX Model

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Status: Authoritative (ELEC-4)  
Series: ELEC-4  
Date: 2026-03-03

## 1) Purpose

ELEC-4 defines playable electrical UX without changing solver semantics:

- diegetic first-person operation
- technician assisted diagnostics
- inspector/admin deep inspection (policy-gated)
- deterministic replay/explanation workflows

All electrical mutation remains `ControlIntent -> Task -> Process`.

## 2) Roles (Policy-Driven)

Role exposure is controlled by epistemic policy/law profile, not hardcoded mode flags.

- `layperson`: coarse energized/trip/alarm indicators
- `technician`: quantized voltage/current/PF and local protection state
- `inspector`: expanded deterministic inspection sections
- `admin/lab`: full policy-allowed inspection + replay tooling

## 3) Tool Taxonomy

Electrical tool types and intended disclosure:

- `tool.test_lamp.basic`: energized yes/no (coarse)
- `tool.multimeter.basic`: voltage (derived), continuity/state cues
- `tool.clamp_meter.basic`: current proxy (derived apparent-load proxy)
- `tool.pf_meter.basic`: PF proxy (`P/S`) quantized
- `tool.insulation_tester.stub`: reserved stub readout path

All values are derived and channel-gated. No tool may read Truth directly.

## 4) Diegetic Channel Contract

Canonical channels:

- `ch.diegetic.elec.energized`
- `ch.diegetic.elec.voltage`
- `ch.diegetic.elec.current_proxy`
- `ch.diegetic.elec.pf`
- `ch.diegetic.elec.trip_warning`
- legacy-compatible:
  - `ch.diegetic.elec.test_lamp`
  - `ch.diegetic.elec.breaker_panel`
  - `ch.diegetic.elec.ground_fault`

## 5) Safety Workflow (LOTO)

Canonical procedure:

1. isolate (`breaker/isolator open`)
2. apply LOTO (`process.elec_apply_loto`)
3. verify de-energized (test lamp/meter channels)
4. perform maintenance/connectivity work
5. remove LOTO (`process.elec_remove_loto`)
6. restore service (`process.elec.flip_breaker` close/reset)

## 6) Explanation Workflow

"Why did it trip?" must be answerable from derived records:

- `FaultState` rows (`elec_fault_states`)
- safety/trip event rows (`elec_trip_events`, `safety_events`)
- decision entries (`decision_logs`)
- compliance context

The response is a deterministic `trip_explanation` artifact.

## 7) UI Workspaces (Progressive Disclosure)

- Diegetic quick panel:
  - energized/trip/alarm glyphs only
- Technician panel:
  - quantized voltage/current/PF and local protection summary
- Inspector/Admin panel (policy-gated):
  - network summary, load ratios, fault/compliance lists, trip explanations

No workspace may bypass epistemic policy.

## 8) Replay / Reenactment UX

Electrical outage replay is integrated with existing reenactment pipeline:

- macro timeline/state view
- meso network + fault/trip overlays
- micro local interaction replay when available

Fidelity negotiation is handled by CTRL; no ELEC-side bypass.

## 9) Invariants

- `INV-NO-TRUTH-IN-UI`
- `INV-ALL-ELEC-ACTIONS-THROUGH-CONTROL`
- `INV-EPILOG-EXPLANATIONS-DERIVED-ONLY`
- `INV-NO-TRUTH-LEAK-IN-INSTRUMENTS`
