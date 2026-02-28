Status: BASELINE
Last Reviewed: 2026-02-28
Version: 1.0.0
Scope: ABS-4 behavioral component substrate.

# Behavioral Components Baseline

## 1) Unified Components
- `ConstraintComponent`: deterministic participant/policy constraints.
- `StateMachineComponent`: deterministic process-triggered transitions.
- `HazardModelComponent`: deterministic accumulation and threshold triggers.
- `ScheduleComponent`: deterministic recurrence and due scheduling.

## 2) Runtime Engines
- `src/core/constraints/constraint_engine.py`
- `src/core/state/state_machine_engine.py`
- `src/core/hazards/hazard_engine.py`
- `src/core/schedule/schedule_engine.py`

## 3) MAT-6 Migration Summary
- Decay/failure accumulation is executed through hazard component APIs.
- Maintenance commitment scheduling uses schedule component APIs.
- Asset maintenance state transitions use state machine component APIs.
- Existing refusal codes and provenance event behavior are preserved.

## 4) Enforcement
RepoX invariants:
- `INV-NO-ADHOC-STATE-FLAGS`
- `INV-NO-ADHOC-HAZARD-LOOPS`
- `INV-NO-ADHOC-SCHEDULERS`
- `INV-CONSTRAINTS-USE-COMPONENT`

AuditX analyzers:
- `AdHocStateFlagSmell`
- `DuplicateSchedulerSmell`
- `HazardLogicDuplicationSmell`

## 5) TestX Coverage
- `test_state_machine_transition_deterministic`
- `test_hazard_threshold_trigger_deterministic`
- `test_schedule_recurrence_deterministic`
- `test_constraint_activation_deterministic`
- `test_migration_equivalence_mat6`

## 6) Gate Snapshot (2026-02-28)
1. RepoX PASS
   - command: `py -3 tools/xstack/repox/check.py --repo-root . --profile STRICT`
   - result: pass (`status=pass`, warnings only; `INV-AUDITX-REPORT-STRUCTURE` trend warning)
2. AuditX run
   - command: `py -3 tools/xstack/auditx/check.py --repo-root . --profile STRICT`
   - result: pass (`status=pass`, warnings/risk findings only, non-gating)
3. TestX PASS
   - command: `py -3 tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset testx.core.state_machine_transition_deterministic,testx.core.hazard_threshold_trigger_deterministic,testx.core.schedule_recurrence_deterministic,testx.core.constraint_activation_deterministic,testx.materials.migration_equivalence_mat6`
   - result: pass (5/5 selected tests passed)
4. strict build PASS
   - command: `py -3 tools/setup/build.py --repo-root . --bundle bundle.base.lab --out build/dist.strict.abs4 --cache on --format json`
   - result: pass (`result=complete`)
5. ui_bind --check PASS
   - command: `py -3 tools/xstack/ui_bind.py --repo-root . --check`
   - result: pass (`result=complete`, `checked_windows=21`)

## 7) Extension Points (INT/POSE/MOB)
- INT portals should attach `StateMachineComponent` for open/closed/sealed transitions and `ConstraintComponent` for sealing participants.
- POSE seat/attachment occupancy should use `ConstraintComponent` hooks with deterministic participant validation.
- MOB guide rails, couplers, and docking should consume `ConstraintComponent` enforcement hooks and avoid ad-hoc constraint loops.
