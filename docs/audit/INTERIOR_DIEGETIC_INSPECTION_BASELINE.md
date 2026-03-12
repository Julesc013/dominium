Status: DERIVED
Last Reviewed: 2026-02-28
Version: 1.0.0
Scope: INT-3 Interior Inspection and Diegetic Instrumentation baseline completion report.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Interior Diegetic Inspection Baseline

## Instrument Channels
- Interior diegetic instrumentation is documented in `docs/interior/INTERIOR_INSPECTION_AND_DIEGETICS.md`.
- Interior instrument type registry coverage includes:
  - `instr.gauge.pressure`
  - `instr.gauge.oxygen`
  - `instr.alarm.smoke`
  - `instr.alarm.flood`
  - `instr.panel.portal_state`
- Diegetic channels integrated and observation-gated:
  - `ch.diegetic.pressure_status`
  - `ch.diegetic.oxygen_status`
  - `ch.diegetic.smoke_alarm`
  - `ch.diegetic.flood_alarm`
  - `ch.diegetic.door_indicator`
- Numeric interior values remain entitlement/law-gated; diegetic defaults use quantized coarse statuses.

## Inspection Sections
- New interior inspection sections integrated into registry + engine:
  - `section.interior.connectivity_summary`
  - `section.interior.portal_state_table`
  - `section.interior.pressure_summary`
  - `section.interior.flood_summary`
  - `section.interior.smoke_summary`
  - `section.interior.flow_summary`
- `inspection_request` target kind support extended for interior targets:
  - `interior_graph`
  - `interior_volume`
  - `interior_portal`
- Snapshot generation remains derived-only and cached by truth anchor + interior target + policy.

## Overlay Behavior
- Procedural overlays (no asset dependency) include:
  - portal state glyphs (open/closed/locked/damaged semantics)
  - interior pressure/flood status visualization from quantized summary sections
  - smoke/alarm glyph markers
- Overlays are deterministic and stable by canonical ordering + hashed IDs.
- Overlay data path is Perceived/inspection-derived only.

## Performance and Degradation
- Instrument readouts are low-cost derived updates.
- Inspection snapshots are RS-5 budgeted and cached.
- Under budget pressure, behavior degrades deterministically to coarse alarm outputs and may refuse high-detail views with explicit refusal metadata.
- No wall-clock dependency introduced.

## Guardrails and Test Coverage
- RepoX invariants integrated:
  - `INV-INTERIOR-STATE-DIEGETIC-GATED`
  - `INV-NO-OMNISCIENT-INTERIOR-UI`
- AuditX analyzers integrated:
  - `InteriorInfoLeakSmell` (`E100_INTERIOR_INFO_LEAK_SMELL`)
  - `AlarmTruthLeakSmell` (`E101_ALARM_TRUTH_LEAK_SMELL`)
- INT-3 TestX coverage added:
  - `test_interior_alarm_thresholds_deterministic`
  - `test_inspection_snapshot_redaction`
  - `test_overlay_ordering_deterministic`
  - `test_no_truth_access_in_instruments`
  - `test_budget_degrade_to_alarms`

## Gate Run Summary
- RepoX (`python tools/xstack/repox/check.py --repo-root . --profile STRICT`):
  - PASS
  - `repox scan passed (files=1019, findings=1)` with non-gating warn in `INV-AUDITX-REPORT-STRUCTURE`.
- AuditX (`python tools/xstack/auditx/check.py --repo-root . --profile STRICT`):
  - run complete / PASS status
  - `auditx scan complete (changed_only=false, findings=998)` (warnings reported).
- TestX INT-3 subset (`python tools/xstack/testx/runner.py --repo-root . --profile STRICT --cache off --subset ...`):
  - PASS for:
    - `testx.interior.interior_alarm_thresholds_deterministic`
    - `testx.interior.inspection_snapshot_redaction`
    - `testx.interior.overlay_ordering_deterministic`
    - `testx.interior.no_truth_access_in_instruments`
    - `testx.interior.budget_degrade_to_alarms`
- TestX full strict (`python tools/xstack/testx/runner.py --repo-root . --profile STRICT --cache on`):
  - FAIL due pre-existing global suite failures outside INT-3 scope (notably broad `create_session_spec refused` fixture failures and unrelated regression fixtures).
- strict profile run (`python tools/xstack/run.py strict --repo-root . --cache on`):
  - REFUSAL (`exit_code=2`)
  - blocking steps include:
    - `01.compatx.check` refusal with existing findings
    - `07.session_boot.smoke` refusal (`session create refused`)
    - `10.testx.run` fail (global strict suite findings)
    - `13.packaging.verify` refusal (`lab build validation refused`)
  - report: `tools/xstack/out/strict/latest/report.json`
- ui_bind (`python tools/xstack/ui_bind.py --repo-root . --check`):
  - PASS (`checked_windows=21`)

## Extension Points
- HVAC/control equipment can expose interior diagnostics and controls via ACT ports/tasks without changing INT-3 epistemic contracts.
- Future INT equipment packs can map instrument channels to machine/panel assemblies while preserving Perceived-only readout rules.
- Advanced per-compartment diagnostics can be added as admin/lab-only sections without changing diegetic defaults.
