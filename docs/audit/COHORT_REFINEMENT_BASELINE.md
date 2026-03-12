Status: DERIVED
Last Reviewed: 2026-02-26
Version: 1.0.0
Scope: CIV-2/4 cohort refinement baseline
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Cohort Refinement Baseline

## Cohort Fields and Policies
- Cohort assembly fields:
  - `cohort_id`, `size`, `faction_id`, `territory_id`, `location_ref`
  - `demographic_tags`, `skill_distribution`
  - `refinement_state`, `created_tick`
- Mapping policy registry:
  - `cohort.map.default`
  - `cohort.map.rank_strict`

## Expand / Collapse Rules
- Expand path:
  - `process.cohort_expand_to_micro`
  - deterministic child IDs from `(cohort_id, slot_index)`
  - parent linkage through `agent.parent_cohort_id`
- Collapse path:
  - `process.cohort_collapse_from_micro`
  - deterministic aggregation over sorted micro rows
  - cohort size reflects collapsed + unexpanded remainder
- Partial expansion:
  - deterministic budgeted selection
  - remaining population preserved in macro cohort

## ROI Integration
- Region management can trigger deterministic cohort expansion/collapse.
- Deterministic priority ordering:
  - `(cohort_id, faction_id, -size, quantized_distance)`
- Budget-limited outcomes emit deterministic run metadata in process results.

## Epistemic Guarantees
- Cohort refinement integrates with LOD epistemic invariance.
- Mapping policy can enforce anonymous micro entities for non-entitled observers.
- Expand/collapse does not grant hidden-state channels by itself.

## Validation Snapshot (2026-02-26)
- RepoX PASS:
  - `py -3 tools/xstack/repox/check.py --repo-root . --profile STRICT`
  - Result: `status=pass` (`repox scan passed`, findings=`1` warn-level only).
- AuditX run:
  - `py -3 tools/auditx/auditx.py scan --repo-root . --changed-only --format json`
  - Result: `result=scan_complete`, findings=`789`.
- TestX PASS (CIV-2 required suite):
  - `py -3 tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset testx.civilisation.cohort_expand_collapse_conservation,testx.civilisation.cohort_expand_deterministic_ids,testx.civilisation.roi_triggers_deterministic_refinement,testx.civilisation.budget_partial_expansion_deterministic,testx.civilisation.epistemic_no_info_gain_from_expand,testx.civilisation.cross_shard_cohort_refusal`
  - Result: `status=pass` (`selected_tests=6`).
- strict build PASS:
  - `C:\Program Files\CMake\bin\cmake.exe --build out/build/vs2026/verify --config Debug --target domino_engine dominium_game dominium_client`
  - Result: build complete for all strict targets.
- `ui_bind --check` PASS:
  - `py -3 tools/xstack/ui_bind.py --repo-root . --check`
  - Result: `result=complete`, `checked_windows=21`.

## Extension Points
- CIV-3: order systems over cohorts and micro agents.
- CIV-4: deterministic demography/procreation transitions.
- Macro population solvers and shard-aware migration strategies.
