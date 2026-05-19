Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# ELEC4 Retro Audit

Status: Drafted for ELEC-4  
Series: ELEC-4  
Date: 2026-03-03

## Scope

Audit focus for Electrical UX/Play Loop:

- direct Truth reads in electrical overlays/instrument views
- UI paths mutating electrical state without `ControlIntent -> Process`
- ad-hoc electrical meter readouts bypassing epistemic policy
- migration/deprecation notes required for UX hardening

## Findings

1. Existing diegetic electrical channels are narrow (`test_lamp`, `breaker_panel`, `ground_fault`) and do not yet expose technician-level voltage/current/PF paths.
2. `process.instrument_tick` already computes multiple meter channels but lacked a complete electrical meter bundle for progressive disclosure UX roles.
3. Existing electrical actions (`connect_wire`, `flip_breaker`, `lockout_tagout`) are process-based; additional operator affordances were not fully surfaced as electrical action templates/workspace actions.
4. Electrical inspection sections existed for faults/protection/compliance, but not the full UX package requested by ELEC-4 (`local_panel_state`, `device_states`, `pf_summary`, `loss_heat_summary`).
5. No canonical `trip_explanation` artifact schema/process existed for deterministic "why did it trip?" explanations.
6. RepoX/AuditX contained ELEC safety invariants/smells, but not explicit ELEC-4 UI leak and direct toggle checks.

## Migration / Deprecation Plan

1. Add electrical UX doctrine and tool/channel taxonomy.
2. Extend tool + instrument registries with deterministic electrical readout channels.
3. Keep all panel/breaker/LOTO/connect operations process-only via control actions and action templates.
4. Add electrical inspection sections and reuse existing inspection cache keying.
5. Introduce deterministic `trip_explanation` schema + process path.
6. Add replay-focused interaction affordances using existing reenactment processes.
7. Add RepoX invariants and AuditX analyzers for:
   - omniscient electrical UI leak
   - direct breaker toggle bypass

## Invariants Upheld

- `INV-CONTROL-PROCESSES-ONLY`
- `INV-NO-TRUTH-LEAK-IN-INSTRUMENTS`
- `INV-INSPECTION-DERIVED-ONLY`
- `INV-ELEC-PROTECTION-THROUGH-SAFETY`
